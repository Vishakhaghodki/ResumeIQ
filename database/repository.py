"""All SQL lives here so routes and services stay clean."""
import json
from collections import Counter

import pandas as pd

from .db import get_db

JSON_FIELDS = ("matched_skills", "missing_skills", "missing_keywords", "suggestions")
INFO_LIST_FIELDS = ("skills", "education", "experience", "projects", "certifications")


def _loads(value, default):
    try:
        return json.loads(value) if value else default
    except (TypeError, ValueError):
        return default


def create_analysis(filename, raw_text, info, job_title, jd_text, result, ats, suggestions, ai):
    db = get_db()
    cur = db.cursor()
    cur.execute("INSERT INTO resumes (filename, raw_text) VALUES (?, ?)", (filename, raw_text))
    resume_id = cur.lastrowid
    cur.execute(
        """INSERT INTO extracted_info
           (resume_id, name, email, phone, skills, education, experience, projects, certifications)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (resume_id, info["name"], info["email"], info["phone"],
         *[json.dumps(info[k]) for k in INFO_LIST_FIELDS]),
    )
    cur.execute("INSERT INTO job_descriptions (title, description) VALUES (?, ?)", (job_title, jd_text))
    job_id = cur.lastrowid
    cur.execute(
        """INSERT INTO analyses
           (resume_id, job_id, match_score, ats_score, skill_score, keyword_score, similarity_score,
            matched_skills, missing_skills, missing_keywords, suggestions, ats_details,
            ai_feedback, ai_mode, ai_provider)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (resume_id, job_id, result["match_score"], ats["score"], result["skill_score"],
         result["keyword_score"], result["similarity_score"],
         json.dumps(result["matched_skills"]), json.dumps(result["missing_skills"]),
         json.dumps(result["missing_keywords"]), json.dumps(suggestions),
         json.dumps({"checks": ats["checks"], "word_count": ats["word_count"], "pages": ats["pages"]}),
         ai["text"], ai["mode"], ai["provider"]),
    )
    analysis_id = cur.lastrowid
    cur.execute(
        "INSERT INTO analysis_history (analysis_id, event, match_score, ats_score) VALUES (?, 'created', ?, ?)",
        (analysis_id, result["match_score"], ats["score"]),
    )
    db.commit()
    return analysis_id


def get_analysis(analysis_id):
    row = get_db().execute(
        """SELECT a.*, r.filename, j.title AS job_title, j.description AS job_description,
                  e.name, e.email, e.phone, e.skills, e.education, e.experience,
                  e.projects, e.certifications
           FROM analyses a
           JOIN resumes r ON r.id = a.resume_id
           JOIN job_descriptions j ON j.id = a.job_id
           JOIN extracted_info e ON e.resume_id = a.resume_id
           WHERE a.id = ?""",
        (analysis_id,),
    ).fetchone()
    if row is None:
        return None
    d = dict(row)
    for key in JSON_FIELDS:
        d[key] = _loads(d.get(key), [])
    d["ats_details"] = _loads(d.get("ats_details"), {"checks": [], "word_count": 0, "pages": 0})
    d["info"] = {
        "name": d.pop("name"), "email": d.pop("email"), "phone": d.pop("phone"),
        **{k: _loads(d.pop(k), []) for k in INFO_LIST_FIELDS},
    }
    return d


def list_analyses(limit=None):
    sql = """SELECT a.id, a.created_at, a.match_score, a.ats_score, a.ai_mode,
                    r.filename, j.title AS job_title, e.name AS candidate
             FROM analyses a
             JOIN resumes r ON r.id = a.resume_id
             JOIN job_descriptions j ON j.id = a.job_id
             JOIN extracted_info e ON e.resume_id = a.resume_id
             ORDER BY a.created_at DESC, a.id DESC"""
    params = ()
    if limit:
        sql += " LIMIT ?"
        params = (int(limit),)
    return [dict(r) for r in get_db().execute(sql, params).fetchall()]


def delete_analysis(analysis_id):
    db = get_db()
    row = db.execute("SELECT resume_id, job_id FROM analyses WHERE id = ?", (analysis_id,)).fetchone()
    if row is None:
        return False
    db.execute("DELETE FROM resumes WHERE id = ?", (row["resume_id"],))          # cascades
    db.execute("DELETE FROM job_descriptions WHERE id = ?", (row["job_id"],))    # cascades
    db.commit()
    return True


def log_event(analysis_id, event):
    db = get_db()
    db.execute(
        """INSERT INTO analysis_history (analysis_id, event, match_score, ats_score)
           SELECT id, ?, match_score, ats_score FROM analyses WHERE id = ?""",
        (event, analysis_id),
    )
    db.commit()


def stats():
    """Dashboard numbers, computed with pandas."""
    df = pd.read_sql_query(
        """SELECT a.id, a.match_score, a.ats_score, a.skill_score, a.keyword_score,
                  a.similarity_score, a.missing_skills, a.created_at, j.title AS job_title
           FROM analyses a JOIN job_descriptions j ON j.id = a.job_id
           ORDER BY a.created_at, a.id""",
        get_db(),
    )
    labels = ["0-39 (Weak)", "40-59 (Fair)", "60-79 (Good)", "80-100 (Strong)"]
    if df.empty:
        return {"total": 0, "avg_match": 0, "avg_ats": 0, "best_match": 0, "averages": {},
                "trend": [], "top_missing": [],
                "distribution": {"labels": labels, "values": [0, 0, 0, 0]}}

    def avg(col):
        return round(float(df[col].mean()), 1)

    counter = Counter()
    for raw in df["missing_skills"]:
        for item in _loads(raw, []):
            counter[item["skill"]] += 1
    buckets = pd.cut(df["match_score"], bins=[-0.1, 39.99, 59.99, 79.99, 100], labels=labels)
    dist = buckets.value_counts().reindex(labels, fill_value=0)
    return {
        "total": int(len(df)),
        "avg_match": avg("match_score"),
        "avg_ats": avg("ats_score"),
        "best_match": round(float(df["match_score"].max()), 1),
        "averages": {"Skill match": avg("skill_score"), "Keywords": avg("keyword_score"),
                     "Text similarity": avg("similarity_score"), "ATS": avg("ats_score")},
        "trend": [
            {"id": int(r.id), "label": f"#{int(r.id)} {str(r.job_title)[:18]}",
             "match": float(r.match_score), "ats": float(r.ats_score)}
            for r in df.itertuples()
        ],
        "top_missing": [{"skill": s, "count": c} for s, c in counter.most_common(10)],
        "distribution": {"labels": labels, "values": [int(v) for v in dist.values]},
    }

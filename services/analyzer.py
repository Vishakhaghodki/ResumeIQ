"""Resume <-> job description matching."""
import re
from collections import Counter

import numpy as np

from .skills import ALL_TERMS, extract_skills

STOP = set("""
a about above after again all also am an and any are as at be because been before being below between
both but by can could did do does doing down during each few for from further had has have having he her
here hers him his how i if in into is it its just me more most my no nor not now of off on once only or
other our out over own same she should so some such than that the their them then there these they this
those through to too under until up very was we were what when where which while who whom why will with
would you your etc including good excellent must hands job company position working using use based across
well new highly plus related like able need needed understanding year years experience work team ability
strong skills knowledge looking role responsibilities requirements required preferred candidate degree
bachelor master opportunity should join apply display etc
""".split())

TOKEN_RE = re.compile(r"[a-z][a-z0-9+#]*(?:[.\-][a-z0-9+#]+)*")


def tokenize(text):
    return TOKEN_RE.findall(text.lower())


def top_keywords(jd_text, n=25):
    counts = Counter(t for t in tokenize(jd_text)
                     if len(t) >= 3 and t not in STOP and t not in ALL_TERMS)
    return [w for w, _ in counts.most_common(n)]


def cosine_similarity(text_a, text_b):
    ca = Counter(t for t in tokenize(text_a) if t not in STOP)
    cb = Counter(t for t in tokenize(text_b) if t not in STOP)
    vocab = sorted(set(ca) | set(cb))
    if not vocab:
        return 0.0
    va = np.array([ca[w] for w in vocab], dtype=float)
    vb = np.array([cb[w] for w in vocab], dtype=float)
    denom = np.linalg.norm(va) * np.linalg.norm(vb)
    return float(va @ vb / denom) if denom else 0.0


def analyze(resume_text, jd_text):
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)

    matched = [s for s in jd_skills if s in resume_skills]
    missing = [{"skill": s, "mentions": c}
               for s, c in sorted(jd_skills.items(), key=lambda kv: -kv[1]) if s not in resume_skills]

    keywords = top_keywords(jd_text)
    resume_tokens = set(tokenize(resume_text))
    missing_keywords = [k for k in keywords if k not in resume_tokens]
    keyword_score = (len(keywords) - len(missing_keywords)) / len(keywords) * 100 if keywords else 0.0

    similarity = min(100.0, cosine_similarity(resume_text, jd_text) * 100 * 1.6)  # scaled: raw cosine is low

    no_jd_skills = not jd_skills
    if no_jd_skills:
        skill_score = keyword_score  # nothing to compare; fall back to keywords
        match = 0.65 * keyword_score + 0.35 * similarity
    else:
        skill_score = len(matched) / len(jd_skills) * 100
        match = 0.5 * skill_score + 0.3 * keyword_score + 0.2 * similarity

    return {
        "match_score": round(match, 1),
        "skill_score": round(skill_score, 1),
        "keyword_score": round(keyword_score, 1),
        "similarity_score": round(similarity, 1),
        "matched_skills": matched,
        "missing_skills": missing,
        "missing_keywords": missing_keywords[:15],
        "no_jd_skills": no_jd_skills,
    }

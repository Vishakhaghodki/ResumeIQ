"""Orchestrates the full analysis: validate -> extract -> parse -> score -> AI -> save."""
from flask import current_app

from database import repository as repo
from utils.validators import validate_job_description, validate_resume_file

from .ai import generate_feedback
from .analyzer import analyze
from .ats import analyze_ats
from .parser import parse_resume
from .pdf_extractor import extract_text
from .suggestions import build_suggestions


def run_analysis(file, job_title, jd_text):
    data = validate_resume_file(file)
    jd_text = validate_job_description(jd_text)
    title = (job_title or "").strip()[:120] or "Untitled role"

    text, pages = extract_text(data)
    info, sections = parse_resume(text)
    result = analyze(text, jd_text)
    ats = analyze_ats(text, info, sections, pages)
    suggestions = build_suggestions(info, result, ats, sections)

    ctx = {
        "job_title": title, "name": info["name"],
        "match_score": result["match_score"], "ats_score": ats["score"],
        "matched": result["matched_skills"],
        "missing": [m["skill"] for m in result["missing_skills"]],
        "missing_keywords": result["missing_keywords"],
        "ats_issues": [c["name"] for c in ats["checks"] if c["status"] != "pass"],
        "resume_excerpt": text[:6000], "jd_excerpt": jd_text[:3000],
    }
    ai = generate_feedback(current_app.config, ctx)
    filename = (file.filename or "resume.pdf")[:200]
    return repo.create_analysis(filename, text, info, title, jd_text, result, ats, suggestions, ai)

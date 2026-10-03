"""ATS (Applicant Tracking System) compatibility checks. Total = 100 points."""
import re

from .parser import BULLET_RE

ACTION_VERBS = set("""
achieved analyzed analysed architected automated built collaborated configured created debugged delivered
deployed designed developed drove enhanced engineered established executed implemented improved increased
integrated launched led managed mentored migrated optimized optimised organized orchestrated oversaw
performed planned prepared reduced refactored resolved scaled shipped solved streamlined supported tested
trained transformed wrote contributed coordinated researched
""".split())

OK_NON_ASCII = set("\u2022\u25cf\u25aa\u25e6\u2013\u2014\u2019\u2018\u201c\u201d\u00b7\u00a0")


def _check(key, name, points, maximum, detail, tip=""):
    status = "pass" if points >= maximum else ("warn" if points > 0 else "fail")
    return {"key": key, "name": name, "status": status, "points": points, "max": maximum,
            "detail": detail, "tip": "" if status == "pass" else tip}


def analyze_ats(text, info, sections, pages):
    words = len(text.split())
    lines = [l for l in text.split("\n") if l.strip()]
    checks = []

    pts = (8 if info["email"] else 0) + (7 if info["phone"] else 0)
    checks.append(_check("contact", "Contact information", pts, 15,
                         f"Email: {'found' if info['email'] else 'missing'}; "
                         f"Phone: {'found' if info['phone'] else 'missing'}",
                         "Put a professional email and a phone number as plain text near the top."))

    for key, label, pts_max, present in [
        ("sec_exp", "Experience or Projects section", 7, "experience" in sections or "projects" in sections),
        ("sec_edu", "Education section", 6, "education" in sections),
        ("sec_skills", "Skills section", 7, "skills" in sections),
    ]:
        checks.append(_check(key, label, pts_max if present else 0, pts_max,
                             "Detected" if present else "No standard heading found",
                             f"Add a clearly labelled heading for: {label.lower()}. ATS software looks for standard headings."))

    if 300 <= words <= 1100:
        pts = 10
    elif 150 <= words < 300 or 1100 < words <= 1600:
        pts = 5
    else:
        pts = 0
    checks.append(_check("length", "Resume length", pts, 10, f"{words} words",
                         "Aim for roughly 300-1100 words (1-2 pages). Trim filler or add detail as needed."))

    pts = 10 if words >= 150 else (5 if words >= 50 else 0)
    checks.append(_check("parsable", "Machine-readable text", pts, 10,
                         "Text extracted cleanly" if pts == 10 else "Very little text extracted",
                         "Export from Word/Google Docs as a text PDF; avoid image-only resumes."))

    bullets = sum(1 for l in lines if BULLET_RE.match(l) and len(BULLET_RE.sub("", l)) > 5)
    pts = 10 if bullets >= 5 else (5 if bullets >= 2 else 0)
    checks.append(_check("bullets", "Bullet points", pts, 10, f"{bullets} bullet lines",
                         "Use short bullet points (not paragraphs) to describe experience and projects."))

    quant = sum(1 for l in lines if re.search(r"\d+\s*%|\$\s?\d|\b\d{2,}\+?\b", l) and len(l) > 20)
    pts = 10 if quant >= 3 else (5 if quant >= 1 else 0)
    checks.append(_check("metrics", "Quantified achievements", pts, 10, f"{quant} lines with numbers/metrics",
                         "Add measurable results (e.g. 'reduced load time by 30%', 'served 500+ users')."))

    verbs = sum(1 for l in lines
                if (BULLET_RE.sub("", l).split() or [""])[0].lower().strip(".,:;") in ACTION_VERBS)
    pts = 10 if verbs >= 5 else (5 if verbs >= 2 else 0)
    checks.append(_check("verbs", "Action verbs", pts, 10, f"{verbs} lines start with strong verbs",
                         "Start bullets with action verbs such as Built, Designed, Implemented, Optimized."))

    odd = sum(1 for ch in text if ord(ch) > 127 and ch not in OK_NON_ASCII and not 0xF000 <= ord(ch) <= 0xF8FF)
    ratio = odd / max(len(text), 1)
    pts = 5 if ratio < 0.01 else (3 if ratio < 0.03 else 0)
    checks.append(_check("format", "Clean characters/formatting", pts, 5, f"{ratio * 100:.1f}% unusual characters",
                         "Avoid icons, fancy symbols, text boxes and multi-column tables."))

    years = len(re.findall(r"\b(?:19|20)\d{2}\b", text))
    pts = 5 if years >= 2 else (2 if years == 1 else 0)
    checks.append(_check("dates", "Dates present", pts, 5, f"{years} year mentions",
                         "Include start/end dates for education, internships and jobs."))

    pts = 5 if pages <= 2 else (3 if pages == 3 else 0)
    checks.append(_check("pages", "Page count", pts, 5, f"{pages} page(s)",
                         "Keep it to 1 page (fresher) or 2 pages maximum."))

    return {"score": round(float(sum(c["points"] for c in checks)), 1),
            "checks": checks, "word_count": words, "pages": pages}

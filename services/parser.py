"""Rule-based resume parser: contact info, skills and section contents."""
import re

from .skills import extract_skills

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?<!\d)(\+?\d[\d\s().\-]{8,17}\d)(?!\d)")
YEAR_RANGE_RE = re.compile(r"(19|20)\d{2}\s*[-\u2013]\s*(19|20)\d{2}")
BULLET_RE = re.compile(r"^\s*[\u2022\u25cf\u25aa\u25e6\u2023\u2043\u00b7\uf0b7\uf0a7\-\*\u2013\u2014>]+\s*")
EDU_RE = re.compile(
    r"b\.?\s?tech|m\.?\s?tech|b\.?\s?e\b|bachelor|master|mba|ph\.?d|diploma|university|college|"
    r"institute|school|cgpa|gpa|b\.?sc|m\.?sc|b\.?ca|m\.?ca", re.I)

HEADINGS = {
    "skills": ["skills", "technical skills", "key skills", "core competencies", "skills & tools",
               "skills and tools", "technical proficiency", "tools & technologies", "technologies"],
    "education": ["education", "academic background", "academic qualifications",
                  "educational qualifications", "education and training"],
    "experience": ["experience", "work experience", "professional experience", "employment history",
                   "work history", "internships", "internship", "internship experience",
                   "relevant experience", "experience & internships"],
    "projects": ["projects", "academic projects", "personal projects", "key projects",
                 "project work", "selected projects", "technical projects"],
    "certifications": ["certifications", "certification", "certificates", "courses",
                       "licenses & certifications", "licenses and certifications",
                       "training & certifications", "courses and certifications"],
    "summary": ["summary", "professional summary", "objective", "career objective", "profile",
                "about me"],
}
HEADING_LOOKUP = {phrase: key for key, phrases in HEADINGS.items() for phrase in phrases}


def _heading_key(line):
    clean = re.sub(r"[^a-z& ]", "", line.lower())
    clean = re.sub(r"\s+", " ", clean).strip()
    if not clean or len(clean) > 40:
        return None
    return HEADING_LOOKUP.get(clean)


def _clean_entries(lines, limit=25):
    out, seen = [], set()
    for line in lines:
        line = BULLET_RE.sub("", line).strip()
        if len(line) < 3 or line.lower() in seen:
            continue
        seen.add(line.lower())
        out.append(line)
        if len(out) >= limit:
            break
    return out


def _find_name(header_lines):
    for line in header_lines[:8]:
        if "@" in line or "http" in line.lower() or sum(c.isdigit() for c in line) >= 4:
            continue
        words = line.replace(",", " ").split()
        if 2 <= len(words) <= 4 and all(re.fullmatch(r"[A-Za-z][A-Za-z.'\-]*", w) for w in words):
            return line.title() if line.isupper() else line
    return "Not detected"


def _find_phone(text):
    for match in PHONE_RE.finditer(text):
        cand = match.group(1).strip()
        digits = re.sub(r"\D", "", cand)
        if 10 <= len(digits) <= 13 and not YEAR_RANGE_RE.match(cand):
            return cand
    return ""


def _find_skills(text, skill_lines):
    found = sorted(extract_skills(text).items(), key=lambda kv: -kv[1])
    skills = [name for name, _ in found]
    known = {s.lower() for s in skills}
    for line in skill_lines:
        line = re.sub(r"^[^:]{1,30}:\s*", "", line)
        for item in re.split(r"[,;|\u2022\u00b7]", line):
            item = BULLET_RE.sub("", item).strip(" .")
            if 2 <= len(item) <= 30 and len(item.split()) <= 3 and item.lower() not in known \
                    and not item.isdigit():
                known.add(item.lower())
                skills.append(item)
    return skills[:40]


def parse_resume(text):
    """Return (info_dict, list_of_detected_section_keys)."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    sections, header, current = {}, [], None
    for line in lines:
        key = _heading_key(line)
        if key:
            current = key
            sections.setdefault(key, [])
        elif current is None:
            header.append(line)
        else:
            sections[current].append(line)

    education = _clean_entries(sections.get("education", []))
    if not education:
        education = _clean_entries([l for l in lines if EDU_RE.search(l)], 6)

    emails = EMAIL_RE.findall(text)
    info = {
        "name": _find_name(header or lines),
        "email": emails[0] if emails else "",
        "phone": _find_phone(text),
        "skills": _find_skills(text, sections.get("skills", [])),
        "education": education,
        "experience": _clean_entries(sections.get("experience", [])),
        "projects": _clean_entries(sections.get("projects", [])),
        "certifications": _clean_entries(sections.get("certifications", [])),
    }
    found_sections = [k for k, v in sections.items() if v]
    return info, found_sections

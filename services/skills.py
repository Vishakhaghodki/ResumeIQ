import re

from .skills_data import ALIASES, SKILLS


def _compile(term):
    # Not preceded/followed by letters, digits, + or # so "java" != "javascript", "sql" != "mysql"
    return re.compile(r"(?<![a-z0-9+#])" + re.escape(term.lower()) + r"(?![a-z0-9+#])")


_PATTERNS = {}
for _skill in SKILLS:
    _PATTERNS.setdefault(_skill, []).append(_compile(_skill))
for _alias, _canon in ALIASES.items():
    _PATTERNS.setdefault(_canon, []).append(_compile(_alias))

# every lowercase term that counts as a "skill" (used to keep skills out of generic keywords)
ALL_TERMS = {s.lower() for s in SKILLS} | set(ALIASES)


def extract_skills(text):
    """Return {canonical_skill: mentions} for taxonomy skills found in text."""
    low = re.sub(r"\s+", " ", text.lower())
    found = {}
    for canon, patterns in _PATTERNS.items():
        count = sum(len(p.findall(low)) for p in patterns)
        if count:
            found[canon] = count
    return found

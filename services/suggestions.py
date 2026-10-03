"""Rule-based, personalised improvement suggestions."""


def build_suggestions(info, result, ats, sections):
    out = []

    def add(priority, text):
        out.append({"priority": priority, "text": text})

    missing = result["missing_skills"]
    if missing:
        top = ", ".join(m["skill"] for m in missing[:6])
        add("high", f"The job description mentions {top}, which your resume doesn't. If you genuinely "
                    "have experience with them, add them to your Skills section and show them in a "
                    "project or experience bullet. Don't list skills you can't discuss in an interview.")
    if result["missing_keywords"]:
        add("medium", "Work these role keywords in naturally, where they are true for you: "
                      + ", ".join(result["missing_keywords"][:8]) + ".")
    if result["match_score"] < 50:
        add("high", "Your overall match is low. Tailor your summary, skills order and top 2-3 projects "
                    "to this specific role instead of sending a generic resume.")
    elif result["match_score"] >= 75:
        add("low", "Strong match. Focus on polishing wording and quantifying your impact.")

    for check in ats["checks"]:
        if check["tip"]:
            add("high" if check["status"] == "fail" else "medium", check["tip"])

    if "summary" not in sections:
        add("low", "Add a 2-3 line professional summary that mirrors the target role's language.")
    if not info["projects"] and not info["experience"]:
        add("high", "Add Projects or Internship experience. Freshers are judged mostly on projects, "
                    "so include 2-3 with tech stack, your role and the outcome.")
    if not info["certifications"]:
        add("low", "Consider adding relevant certifications or online courses to back up key skills.")
    if info["name"] == "Not detected":
        add("medium", "Put your full name as the first line so it is detected reliably.")

    order = {"high": 0, "medium": 1, "low": 2}
    return sorted(out, key=lambda s: order[s["priority"]])

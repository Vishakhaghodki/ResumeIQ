"""End-to-end smoke test: python tests/smoke_test.py  (uses a temporary database)"""
import io
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app  # noqa: E402
from config import Config  # noqa: E402


def make_pdf(lines):
    esc = lambda s: s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    content = "BT /F1 10 Tf 40 780 Td 13 TL\n" + "".join(f"({esc(l)}) Tj T*\n" for l in lines) + "ET"
    objs = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R "
        "/Resources << /Font << /F1 5 0 R >> >> >>",
        f"<< /Length {len(content)} >>\nstream\n{content}\nendstream",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out, offsets = b"%PDF-1.4\n", []
    for i, o in enumerate(objs, 1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n{o}\nendobj\n".encode()
    xref = len(out)
    out += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode()
    out += "".join(f"{o:010d} 00000 n \n" for o in offsets).encode()
    out += f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode()
    return out


RESUME = """Rahul Sharma
rahul.sharma@example.com | +91 98765 43210
SUMMARY
B.Tech student passionate about backend development.
EDUCATION
B.Tech in Computer Science, ABC Institute of Technology, 2022 - 2026, CGPA 8.4
SKILLS
Languages: Python, Java, SQL, JavaScript
Frameworks: Flask, Django, Pandas, NumPy
Tools: Git, GitHub, Docker, Linux
PROJECTS
- Built a REST API with Flask and SQLite serving 500+ users
- Developed a sales dashboard using Pandas and Matplotlib, reduced reporting time by 40%
- Implemented a machine learning model with Scikit-learn achieving 92% accuracy
EXPERIENCE
Python Developer Intern, XYZ Technologies, 2025
- Designed and deployed 12 REST API endpoints used by 3 internal teams
- Optimized SQL queries and improved response time by 35%
- Collaborated with a team of 5 engineers using Agile and Git
CERTIFICATIONS
- AWS Cloud Practitioner, 2025
- Python for Data Science, Coursera, 2024
""".strip().split("\n")

JD = ("We are hiring a Python Backend Developer. Requirements: strong Python, Flask or Django, REST API design, "
      "PostgreSQL, Docker, AWS, Kubernetes, CI/CD pipelines, unit testing with Pytest. Experience with Agile teams.")


def main():
    tmp = tempfile.mkdtemp()

    class TestConfig(Config):
        DATABASE = os.path.join(tmp, "test.db")
        TESTING = True
        ANTHROPIC_API_KEY = ""
        OPENAI_API_KEY = ""

    client = create_app(TestConfig).test_client()

    for url in ["/", "/analyze", "/dashboard", "/history", "/api/health", "/api/stats"]:
        assert client.get(url).status_code == 200, url
    print("pages OK")

    pdf = make_pdf(RESUME)
    r = client.post("/api/analyze", data={"resume": (io.BytesIO(pdf), "resume.pdf"),
                                           "job_title": "Python Backend Developer", "job_description": JD},
                    content_type="multipart/form-data")
    assert r.status_code == 201, r.get_data(as_text=True)
    a = r.get_json()["analysis"]
    aid = a["id"]
    print("name:", a["info"]["name"], "| email:", a["info"]["email"], "| phone:", a["info"]["phone"])
    print("match:", a["match_score"], "| ats:", a["ats_score"], "| mode:", a["ai_mode"])
    print("matched:", a["matched_skills"])
    print("missing:", [m["skill"] for m in a["missing_skills"]])
    assert a["info"]["email"] == "rahul.sharma@example.com" and a["info"]["name"] == "Rahul Sharma"
    assert a["info"]["phone"] and a["info"]["skills"] and a["info"]["projects"] and a["info"]["certifications"]
    assert a["info"]["education"] and a["info"]["experience"]
    assert "Kubernetes" in [m["skill"] for m in a["missing_skills"]]
    assert a["ai_mode"] == "demo"

    assert client.get(f"/result/{aid}").status_code == 200
    rep = client.get(f"/api/analyses/{aid}/report")
    assert rep.status_code == 200 and "attachment" in rep.headers["Content-Disposition"]
    assert client.get("/history").status_code == 200
    s = client.get("/api/stats").get_json()
    assert s["total"] == 1 and s["top_missing"], s
    assert len(client.get("/api/analyses").get_json()["analyses"]) == 1
    print("result/report/stats/history OK")

    def post(**kw):
        d = {"job_title": "x", "job_description": JD}
        files = kw.pop("files", {"resume": (io.BytesIO(pdf), "resume.pdf")})
        d.update(kw)
        d.update(files)
        return client.post("/api/analyze", data=d, content_type="multipart/form-data")

    assert post(job_description="short").status_code == 400
    assert post(files={"resume": (io.BytesIO(b"hello"), "resume.txt")}).status_code == 400
    assert post(files={"resume": (io.BytesIO(b"not a pdf"), "fake.pdf")}).status_code == 400
    assert post(files={}).status_code == 400
    assert client.get("/api/analyses/999").status_code == 404
    assert client.get("/result/999").status_code == 404
    print("validation/errors OK")

    assert client.delete(f"/api/analyses/{aid}").status_code == 200
    assert client.get(f"/api/analyses/{aid}").status_code == 404
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()

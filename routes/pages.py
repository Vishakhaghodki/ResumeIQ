from flask import Blueprint, abort, render_template

from database import repository as repo

pages_bp = Blueprint("pages", __name__)


@pages_bp.get("/")
def index():
    return render_template("index.html")


@pages_bp.get("/analyze")
def analyze():
    return render_template("analyze.html")


@pages_bp.get("/result/<int:analysis_id>")
def result(analysis_id):
    analysis = repo.get_analysis(analysis_id)
    if not analysis:
        abort(404)
    return render_template("result.html", a=analysis)


@pages_bp.get("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@pages_bp.get("/history")
def history():
    return render_template("history.html", rows=repo.list_analyses())

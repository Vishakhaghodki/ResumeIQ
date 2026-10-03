from flask import Blueprint, Response, jsonify, render_template, request

from database import repository as repo
from services.pipeline import run_analysis
from utils.errors import AppError

api_bp = Blueprint("api", __name__)


@api_bp.get("/health")
def health():
    from flask import current_app
    from services.ai import ai_status
    return jsonify({"status": "ok", "ai": ai_status(current_app.config)})


@api_bp.post("/analyze")
def analyze():
    analysis_id = run_analysis(
        request.files.get("resume"),
        request.form.get("job_title", ""),
        request.form.get("job_description", ""),
    )
    return jsonify({"id": analysis_id, "redirect": f"/result/{analysis_id}",
                    "analysis": repo.get_analysis(analysis_id)}), 201


@api_bp.get("/analyses")
def list_analyses():
    return jsonify({"analyses": repo.list_analyses(request.args.get("limit", type=int))})


@api_bp.get("/analyses/<int:analysis_id>")
def get_analysis(analysis_id):
    analysis = repo.get_analysis(analysis_id)
    if not analysis:
        raise AppError("Analysis not found.", 404)
    return jsonify(analysis)


@api_bp.delete("/analyses/<int:analysis_id>")
def delete_analysis(analysis_id):
    if not repo.delete_analysis(analysis_id):
        raise AppError("Analysis not found.", 404)
    return jsonify({"deleted": analysis_id})


@api_bp.get("/analyses/<int:analysis_id>/report")
def download_report(analysis_id):
    analysis = repo.get_analysis(analysis_id)
    if not analysis:
        raise AppError("Analysis not found.", 404)
    repo.log_event(analysis_id, "report_downloaded")
    html = render_template("report.html", a=analysis)
    return Response(html, mimetype="text/html", headers={
        "Content-Disposition": f'attachment; filename="resumeiq_report_{analysis_id}.html"'})


@api_bp.get("/stats")
def stats():
    return jsonify(repo.stats())

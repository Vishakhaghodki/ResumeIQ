import logging
import os

from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import HTTPException

from config import Config
from database.db import close_db, init_db
from routes.api import api_bp
from routes.pages import pages_bp
from services.ai import ai_status
from utils.errors import AppError


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)
    logging.basicConfig(level=logging.INFO)

    init_db(app)
    app.teardown_appcontext(close_db)
    app.register_blueprint(pages_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.context_processor
    def inject_ai_status():
        return {"ai_status": ai_status(app.config)}

    @app.template_filter("score_class")
    def score_class(value):
        value = value or 0
        return "good" if value >= 75 else "warn" if value >= 50 else "bad"

    def respond(message, status):
        if request.path.startswith("/api/"):
            return jsonify({"error": message}), status
        return render_template("error.html", message=message, status=status), status

    @app.errorhandler(AppError)
    def handle_app_error(err):
        return respond(err.message, err.status)

    @app.errorhandler(HTTPException)
    def handle_http_error(err):
        if err.code == 413:
            return respond("File too large. Maximum size is 5 MB.", 413)
        return respond(err.description or err.name, err.code)

    @app.errorhandler(Exception)
    def handle_unexpected(err):
        app.logger.exception("Unhandled error: %s", err)
        return respond("Something went wrong on our side. Please try again.", 500)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", 5000)),
            debug=os.getenv("FLASK_DEBUG", "0") == "1")

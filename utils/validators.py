from .errors import AppError

MAX_JD_CHARS = 15000
MIN_JD_CHARS = 50


def validate_resume_file(file):
    """Return the PDF bytes, or raise AppError."""
    if file is None or not file.filename:
        raise AppError("Please upload a PDF resume.")
    if not file.filename.lower().endswith(".pdf"):
        raise AppError("Only PDF files are supported.")
    data = file.read()
    if not data:
        raise AppError("The uploaded file is empty.")
    if not data.lstrip().startswith(b"%PDF"):
        raise AppError("This file doesn't look like a valid PDF.")
    return data


def validate_job_description(text):
    text = (text or "").strip()
    if len(text) < MIN_JD_CHARS:
        raise AppError(f"Job description is too short (minimum {MIN_JD_CHARS} characters).")
    if len(text) > MAX_JD_CHARS:
        raise AppError(f"Job description is too long (maximum {MAX_JD_CHARS} characters).")
    return text

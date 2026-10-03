import re
from io import BytesIO

from pypdf import PdfReader

from utils.errors import AppError


def extract_text(data: bytes):
    """Return (text, page_count) from PDF bytes."""
    try:
        reader = PdfReader(BytesIO(data))
        if reader.is_encrypted:
            try:
                ok = reader.decrypt("")
            except Exception:
                ok = 0
            if not ok:
                raise AppError("This PDF is password-protected. Please upload an unprotected copy.")
        pages = [(page.extract_text() or "") for page in reader.pages]
        page_count = len(reader.pages)
    except AppError:
        raise
    except Exception:
        raise AppError("Could not read this PDF. It may be corrupted.")

    text = "\n".join(pages).replace("\r", "\n").replace("\x00", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if len(text.split()) < 30:
        raise AppError(
            "Almost no text could be extracted. The PDF may be a scanned image "
            "(OCR is not supported). Please upload a text-based PDF.", 422)
    return text, page_count

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    DATABASE = os.getenv("DATABASE_PATH", str(BASE_DIR / "instance" / "resumeiq.db"))
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB upload limit

    # AI configuration (keys are read ONLY from environment variables)
    AI_PROVIDER = os.getenv("AI_PROVIDER", "auto").lower()
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5-5")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

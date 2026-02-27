from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # LLM providers
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"

    openai_api_key: str | None = None

    anthropic_api_key: str | None = None

    # Infraestrutura local
    poppler_path: str = r"C:\poppler\poppler-23.11.0\poppler-23.11.0\Library\bin"
    tesseract_cmd: str = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


settings = Settings()
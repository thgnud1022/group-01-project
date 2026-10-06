import os
import re
from pydantic_settings import BaseSettings


def _clean_supabase_url(raw_url: str) -> str:
    cleaned = raw_url.strip().strip("'\"").strip()
    if cleaned and not cleaned.startswith("http://") and not cleaned.startswith("https://"):
        cleaned = f"https://{cleaned}"
    return cleaned.rstrip("/")


def _resolve_default_supabase_url() -> str:
    raw_env = os.getenv("SUPABASE_URL")
    if raw_env and raw_env.strip():
        return _clean_supabase_url(raw_env)
    db_url = os.getenv("DATABASE_URL", "")
    match = re.search(r"@(?:db\.|aws-[0-9]+-[a-z0-9-]+\.pooler\.)([a-z0-9_-]+)\.supabase\.co", db_url)
    if match:
        return f"https://{match.group(1)}.supabase.co"
    return "https://sthjkfssmvoswocnttrw.supabase.co"


_base_supabase_url = _resolve_default_supabase_url()


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://app:app-local-password@localhost:5432/procurement_db")
    SUPABASE_URL: str = _base_supabase_url
    SUPABASE_JWKS_URL: str = os.getenv("SUPABASE_JWKS_URL", f"{_base_supabase_url}/auth/v1/.well-known/jwks.json")
    JWT_ISSUER: str = os.getenv("JWT_ISSUER", f"{_base_supabase_url}/auth/v1")
    JWT_AUDIENCE: str = os.getenv("JWT_AUDIENCE", "authenticated")
    JWT_ALGORITHM: str = "ES256"

    JWT_SECRET: str = os.getenv("JWT_SECRET", "super-secret-key-for-ai-procurement-system-2026")
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "gemini")
    LLM_API_KEY: str = os.getenv("GEMINI_API_KEY", os.getenv("LLM_API_KEY", ""))
    LLM_MODEL: str = os.getenv("GEMINI_MODEL", os.getenv("LLM_MODEL", "gemini-3.8-flash"))
    LLM_TIMEOUT: float = float(os.getenv("LLM_TIMEOUT", "10.0"))

    class Config:
        env_file = ".env"


settings = Settings()

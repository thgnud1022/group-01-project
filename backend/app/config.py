import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://app:app-local-password@localhost:5432/procurement_db")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super-secret-key-for-ai-procurement-system-2026")
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "mock")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")

    class Config:
        env_file = ".env"

settings = Settings()

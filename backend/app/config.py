"""
Application configuration loaded from environment variables.
All settings are defined here using Pydantic BaseSettings.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central configuration for the Groww Market Intelligence RAG backend.
    Values are loaded from environment variables or a .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Database ──────────────────────────────────────────────────────
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/rag_grow.db"

    # ── Vector DB & Snapshots ─────────────────────────────────────────
    CHROMA_PERSIST_DIR: str = "./data/chromadb"
    SNAPSHOT_DIR: str = "./data/snapshots"

    # ── GROK LLM ──────────────────────────────────────────────────────
    GROK_API_KEY: str = ""
    GROK_API_BASE_URL: str = "https://api.x.ai/v1"
    GROK_MODEL_NAME: str = "grok-beta"

    # ── Embedding Model ───────────────────────────────────────────────
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    # ── JWT Auth ──────────────────────────────────────────────────────
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_EXPIRY_HOURS: int = 1

    # ── Scraping ──────────────────────────────────────────────────────
    SCRAPE_INTERVAL_MINUTES: int = 15
    SCRAPE_TIMEOUT_SECONDS: int = 30
    SCRAPE_MAX_CONCURRENT: int = 5

    # ── Admin Seed Credentials ────────────────────────────────────────
    ADMIN_DEFAULT_USERNAME: str = "admin"
    ADMIN_DEFAULT_PASSWORD: str = "admin"

    # ── CORS ──────────────────────────────────────────────────────────
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,https://frontend-pranjali3.vercel.app"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


@lru_cache
def get_settings() -> Settings:
    """
    Return a cached Settings instance.
    Use this as a FastAPI dependency: `Depends(get_settings)`.
    """
    return Settings()


# Module-level singleton for use outside FastAPI dependency injection
settings = get_settings()

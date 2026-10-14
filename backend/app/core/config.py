from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://research_assistant:research_assistant@localhost:5432/research_assistant"

    gemini_api_key: str = ""
    voyage_api_key: str = ""
    semantic_scholar_api_key: str = ""

    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 60 * 24 * 7

    gemini_model: str = "gemini-flash-latest"
    voyage_embedding_model: str = "voyage-3"
    voyage_embedding_dim: int = 1024

    upload_dir: str = "uploads"

    cors_origins: list[str] = ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()

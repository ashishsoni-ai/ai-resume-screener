from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",       # ignore unknown keys in .env
    )

    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"
    db_url: str = "sqlite:///./resume_screener.db"
    max_file_size_mb: int = 5
    upload_dir: str = "uploads"


settings = Settings()
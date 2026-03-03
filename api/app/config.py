from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database (Postgres)
    database_url: str = ""

    # GCP Cloud Storage
    gcp_project_id: str = ""
    gcs_bucket: str = "ai-home-styling-poc"

    # OpenRouter
    openrouter_api_key: str = ""

    # Google Cloud Vision
    google_cloud_api_key: str = ""

    # Redis
    redis_url: str = "redis://localhost:6379"

    # App
    api_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
    )


settings = Settings()

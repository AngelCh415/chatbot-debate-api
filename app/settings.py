"""App settings and environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App settings."""

    DEBUG: bool = True  # Only in local development

    # Feature flag: use AI or not, default: False
    USE_AI: bool = False

    # OpenAI
    OPENAI_API_KEY: str | None = None
    # Model to use, default: gpt-4o-mini
    OPENAI_MODEL: str = "gpt-4o-mini"
    # Timeout for OpenAI requests, default: 15 seconds
    OPENAI_TIMEOUT: int = 15

    # Answer generation parameters
    # Max tokens for the response, default: 400
    MAX_TOKENS: int = 400
    # Temperature for the response, default: 0.6
    TEMPERATURE: float = 0.6

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()

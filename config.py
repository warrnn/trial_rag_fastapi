from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    EMBEDDING_MODEL_NAME: str
    GEMINI_API_KEY: str
    GEMINI_GENERATOR_MODEL: str


ENV = Settings()

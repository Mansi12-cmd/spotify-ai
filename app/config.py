from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    GROQ_API_KEY: str
    GROQ_MODEL: str = "openai/gpt-oss-20b"
    SPOTIFY_CLIENT_ID: str
    SPOTIFY_CLIENT_SECRET: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
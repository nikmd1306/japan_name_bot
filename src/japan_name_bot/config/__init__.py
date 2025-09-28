from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: str
    CHANNEL_ID: str
    DATABASE_URL: str
    DEFAULT_PROVIDER: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()  # type: ignore[reportCallIssue]

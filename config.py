from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    imagekit_private_key: str
    imagekit_url_endpoint: str
    imagekit_public_key: str
    gemini_api_key: str
    openrouter_api_key: str
    frontend_url: str = "http://localhost:3000"
    database_url: str = "sqlite+aiosqlite:///./dawa.db"


settings = Settings()  # type:ignore

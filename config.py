from email.mime import image

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    imagekit_private_key: str
    imagekit_url_endpoint: str
    imagekit_public_key: str


settings = Settings()  # type:ignore

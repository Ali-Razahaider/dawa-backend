from datetime import datetime, UTC

from pydantic import Field, BaseModel, ConfigDict


class UserInput(BaseModel):
    image_url: str = Field(min_length=1, max_length=200)
    content: str | None = Field(default=None)


class Response(BaseModel):
    pass

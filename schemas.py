import string

from pydantic import Field, BaseModel, ConfigDict


class UserInput(BaseModel):
    image_url: str = Field(min_length=1, max_length=200)

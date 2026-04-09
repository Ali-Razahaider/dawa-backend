from pydantic import BaseModel, Field


class UserInput(BaseModel):
    image_url: str = Field(min_length=1, max_length=200)
    content: str | None = Field(default=None)


class MedicineItem(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    dosage: str | None = Field(default=None, max_length=120)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    raw_line: str | None = Field(default=None, max_length=300)


class PrescriptionCreateResponse(BaseModel):
    id: int
    image_url: str
    caption: str | None = None
    medicines: list[MedicineItem] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class Response(PrescriptionCreateResponse):
    pass

from pydantic import BaseModel, Field
from datetime import datetime


class UserInput(BaseModel):
    image_url: str = Field(min_length=1, max_length=200)
    content: str | None = Field(default=None)


class MedicineItem(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    dosage: str | None = Field(default=None, max_length=120)
    frequency: str | None = Field(default=None, max_length=120)
    duration: str | None = Field(default=None, max_length=120)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    raw_line: str | None = Field(default=None, max_length=300)


class ExtractedMedicines(BaseModel):
    medicines: list[MedicineItem] = Field(default_factory=list)


class PrescriptionRecord(BaseModel):
    id: int
    extracted_medicines: ExtractedMedicines
    created_at: datetime


class PrescriptionsListResponse(BaseModel):
    prescriptions: list[PrescriptionRecord] = Field(default_factory=list)


class ApiErrorResponse(BaseModel):
    code: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=300)
    details: dict[str, str | int | float | bool | None] | None = None

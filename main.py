from contextlib import asynccontextmanager
import json
from pathlib import Path
from time import time
from typing import Annotated
from uuid import uuid4

from fastapi import Depends, FastAPI, File, Request, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from database import Base, engine, get_db
from models import Prescription
from schemas import ExtractedMedicines, PrescriptionRecord, PrescriptionsListResponse
from services.gemini_service import generate_prescription
from config import settings


requests_counts = {}
RATE_LIMIT = 1
TIME_WINDOW = 60  # Max 1 request per minute
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_UPLOAD_SIZE_BYTES = 5 * 1024 * 1024


@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)
Path("uploads").mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


def validate_prescription_image(image: UploadFile, file_bytes: bytes) -> None:
    if not image.filename:
        raise HTTPException(status_code=400, detail="Image filename is required.")

    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=415,
            detail="Only JPEG, PNG, and WEBP images are supported.",
        )

    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded image is empty.")

    if len(file_bytes) > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail="Image size must be 5 MB or less.",
        )


def upload_image_local(file_bytes: bytes, file_name: str | None) -> str:
    uploads_dir = Path("uploads")
    suffix = Path(file_name).suffix.lower() if file_name else ""
    if not suffix:
        suffix = ".jpg"

    stored_name = f"{uuid4().hex}{suffix}"
    output_path = uploads_dir / stored_name

    try:
        output_path.write_bytes(file_bytes)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to save uploaded image.")

    return f"/uploads/{stored_name}"


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path != "/prescription" or request.method == "OPTIONS":
            return await call_next(request)
        client_ip = request.client.host if request.client else "unknown"
        current_time = time()

        if client_ip not in requests_counts:
            requests_counts[client_ip] = []

        requests_counts[client_ip] = [
            t for t in requests_counts[client_ip] if current_time - t < TIME_WINDOW
        ]

        if len(requests_counts[client_ip]) >= RATE_LIMIT:
            # Calculate seconds until the oldest request expires
            oldest_request_time = requests_counts[client_ip][0]
            retry_after = int(TIME_WINDOW - (current_time - oldest_request_time))
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests. Please try again later.",
                    "retry_after": max(1, retry_after),
                },
            )
        requests_counts[client_ip].append(current_time)
        response = await call_next(request)
        return response


app.add_middleware(RateLimitMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        settings.frontend_url,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return "Hello!!"


@app.post("/prescription", response_model=ExtractedMedicines)
async def create_prescription(
    db: Annotated[AsyncSession, Depends(get_db)],
    image: UploadFile = File(...),
):

    file_bytes = await image.read()
    validate_prescription_image(image=image, file_bytes=file_bytes)
    image_url = "/uploads/img1"

    extracted_medicines = await generate_prescription(image_bytes=file_bytes)

    prescription = Prescription(
        image_url=image_url,
        gemini_response=extracted_medicines.model_dump_json(),
    )
    db.add(prescription)
    await db.commit()
    await db.refresh(prescription)

    return extracted_medicines


@app.get("/prescriptions", response_model=PrescriptionsListResponse)
async def list_prescriptions(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(Prescription).order_by(Prescription.created_at.desc())
    )
    rows = result.scalars().all()

    records: list[PrescriptionRecord] = []
    for row in rows:
        payload = {"medicines": []}
        if row.gemini_response:
            try:
                payload = json.loads(row.gemini_response)
            except json.JSONDecodeError:
                payload = {"medicines": []}

        records.append(
            PrescriptionRecord(
                id=row.id,
                extracted_medicines=ExtractedMedicines(**payload),
                created_at=row.created_at,
            )
        )

    return PrescriptionsListResponse(prescriptions=records)


@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request, exc: StarletteHTTPException):
    message = (
        exc.detail
        if exc.detail
        else "An unexpected error occurred. Please try again later."
    )
    if request.url.path.startswith("/prescription"):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": message},
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": "Resource Not Found"},
    )

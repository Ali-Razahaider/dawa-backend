from fastapi import FastAPI, File, Form, Request, UploadFile, HTTPException
from contextlib import asynccontextmanager
from database import Base, engine
from services.imagekit_service import upload_file
from starlette.exceptions import HTTPException as StarletteHTTPException
from services.gemini_service import generate_prescription
from fastapi.responses import JSONResponse
from time import time
from starlette.middleware.base import BaseHTTPMiddleware


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


app = FastAPI()


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


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path != "/prescription":
            return await call_next(request)
        client_ip = request.client.host if request.client else "unknown"
        current_time = time()

        if client_ip not in requests_counts:
            requests_counts[client_ip] = []

        requests_counts[client_ip] = [
            t for t in requests_counts[client_ip] if current_time - t < TIME_WINDOW
        ]

        if len(requests_counts[client_ip]) >= RATE_LIMIT:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please try again later."},
            )
        requests_counts[client_ip].append(current_time)
        response = await call_next(request)
        return response


app.add_middleware(RateLimitMiddleware)


@app.get("/")
def home():
    return "Hello!!"


@app.post("/prescription")
async def create_prescription(
    image: UploadFile = File(...),
    caption: str | None = Form(default=None, max_length=300),
):

    file_bytes = await image.read()
    validate_prescription_image(image=image, file_bytes=file_bytes)

    image_url = await upload_file(
        file_bytes=file_bytes,
        file_name=image.filename or "prescription.jpg",
    )

    response = await generate_prescription(image_url=image_url)

    return response


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

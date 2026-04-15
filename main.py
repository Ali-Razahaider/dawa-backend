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


@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI()


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
    caption: str | None = Form(default=None),
):

    file_bytes = await image.read()

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

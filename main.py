from fastapi import FastAPI, File, Form, Request, UploadFile
from contextlib import asynccontextmanager
from database import Base, engine
from services.imagekit_service import upload_file
from starlette.exceptions import HTTPException as StarletteHTTPException
from services.gemini_service import generate_prescription
from fastapi.responses import JSONResponse


@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI()


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

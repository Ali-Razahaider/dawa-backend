from fastapi import FastAPI, File, Form, UploadFile
from schemas import Response
from contextlib import asynccontextmanager
from database import Base, engine
from services.imagekit_service import upload_file


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


@app.post("/prescription", response_model=Response)
async def create_prescription(
    image: UploadFile = File(...),
    caption: str | None = Form(default=None),
):

    file_bytes = await image.read()

    image_url = await upload_file(
        file_bytes=file_bytes,
        file_name=image.filename or "prescription.jpg",
    )

    return Response(
        id=0,
        image_url=image_url,
        caption=caption,
        medicines=[],
        warnings=["Gemini analysis will be added next."],
    )

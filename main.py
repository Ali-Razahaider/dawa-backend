from fastapi import FastAPI, File, Form, UploadFile
from schemas import Response
from contextlib import asynccontextmanager
from database import Base, engine


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
    return Response(
        id=0,
        image_url="pending-imagekit-upload",
        caption=caption,
        medicines=[],
        warnings=["Image upload and Gemini analysis will be added next."],
    )

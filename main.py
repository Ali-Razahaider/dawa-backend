from fastapi import FastAPI, File, Form, UploadFile
from schemas import PrescriptionCreateResponse
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


@app.post("/prescription", response_model=PrescriptionCreateResponse)
async def create_prescription(
    image: UploadFile = File(...),
    caption: str | None = Form(default=None),
):
    # Contract-only response for now. ImageKit upload and Gemini analysis
    # will be added in the next implementation steps.
    return PrescriptionCreateResponse(
        id=0,
        image_url="pending-imagekit-upload",
        caption=caption,
        medicines=[],
        warnings=["Contract ready: upload and analysis not implemented yet."],
    )

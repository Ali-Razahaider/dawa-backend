from fastapi import FastAPI
from schemas import UserInput, Response
from contextlib import asynccontextmanager
from database import get_db, AsyncSession, Base, engine


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
def create_prescription(prescription: UserInput):
    pass

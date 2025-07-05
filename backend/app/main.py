from fastapi import FastAPI
from app.api import api_router
from app.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.lifespan import shut_down, start_up


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_up()
    yield
    shut_down()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:1860"] for stricter security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI backend!"}


app.include_router(api_router)

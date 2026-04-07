from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, exchange_rates, interest_rates, subscriptions, chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title="Carry Trade Helper API",
    description="API for carry trade analysis with AI-powered recommendations",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(exchange_rates.router)
app.include_router(interest_rates.router)
app.include_router(subscriptions.router)
app.include_router(chat.router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Carry Trade Helper API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
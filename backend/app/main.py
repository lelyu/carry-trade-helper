from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import exchange_rates, interest_rates

app = FastAPI(
    title="Carry Trade Helper API",
    description="Exchange rates and interest rates for carry trade analysis",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(exchange_rates.router)
app.include_router(interest_rates.router)


@app.get("/")
async def root():
    return {
        "message": "Carry Trade Helper API",
        "version": "0.2.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
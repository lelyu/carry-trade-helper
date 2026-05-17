import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import exchange_rates, interest_rates
from app.tasks.scheduler import prefetch_all, scheduler_loop

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting background prefetch scheduler")
    asyncio.create_task(prefetch_all())
    task = asyncio.create_task(
        scheduler_loop(interval=settings.PREFETCH_INTERVAL_SECONDS)
    )
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    logger.info("Scheduler stopped")


app = FastAPI(
    title="Carry Trade Helper API",
    description="Exchange rates and interest rates for carry trade analysis",
    version="0.3.0",
    lifespan=lifespan,
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
        "version": "0.3.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
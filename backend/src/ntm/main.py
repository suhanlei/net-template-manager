import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ntm.core.config import get_settings
from ntm.core.database import init_db
from ntm.api.v1 import api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database...")
    init_db()
    settings = get_settings()
    logger.info(f"NTM started — debug={settings.debug}")
    yield
    logger.info("NTM shutting down")


app = FastAPI(
    title="Net Template Manager",
    description="Network Configuration Template Version Management System",
    version="0.1.0",
    lifespan=lifespan,
)

# Init DB on import (idempotent)
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "ntm.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
    )

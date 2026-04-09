from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.api import api_router
from app.core import settings
from app.core import setup_logging

# Project root for optional static mounting
project_root = Path(__file__).resolve().parent.parent


@asynccontextmanager
async def lifespan(application: FastAPI):
    setup_logging()
    yield


def get_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        lifespan=lifespan
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(api_router, prefix=settings.API_V1_STR)

    return application


app = get_application()


# Keep a simple JSON health endpoint
@app.get("/health")
async def health():
    return JSONResponse({"status": "ok", "message": "API is running"})

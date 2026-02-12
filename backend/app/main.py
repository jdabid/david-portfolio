"""
FastAPI application factory.
Creates the app instance, registers middleware, routers, and startup/shutdown events.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.infrastructure.database import engine
from app.infrastructure.redis import redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup and shutdown events."""
    # Startup
    await redis_client.ping()
    yield
    # Shutdown
    await engine.dispose()
    await redis_client.close()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins.split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check
    @app.get("/api/health", tags=["infra"])
    async def health_check():
        return {"status": "healthy", "service": settings.app_name}

    return app


app = create_app()

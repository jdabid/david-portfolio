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
    # Startup — import handlers to register them with the mediator
    import app.features.profile.commands.update_profile  # noqa: F401
    import app.features.profile.queries.get_profile  # noqa: F401
    import app.features.profile.queries.get_skills  # noqa: F401
    import app.features.projects.commands.create_project  # noqa: F401
    import app.features.projects.queries.list_projects  # noqa: F401
    import app.features.projects.queries.get_project_detail  # noqa: F401
    import app.features.contact.commands.send_message  # noqa: F401

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

    # Register feature routers
    from app.features.profile.router import router as profile_router
    from app.features.projects.router import router as projects_router
    from app.features.contact.router import router as contact_router

    app.include_router(profile_router)
    app.include_router(projects_router)
    app.include_router(contact_router)

    return app


app = create_app()

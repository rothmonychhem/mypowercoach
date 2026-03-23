from fastapi import FastAPI

from app.api.router import api_router
from app.bootstrap import bootstrap_application
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    bootstrap_application()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Adaptive coaching backend for myPowerCoach.",
    )
    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_app()

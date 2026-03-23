from fastapi import APIRouter

from app.api.routes import athletes, auth, coaching, health, programs

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(athletes.router, prefix="/athletes", tags=["athletes"])
api_router.include_router(programs.router, prefix="/programs", tags=["programs"])
api_router.include_router(coaching.router, prefix="/coaching", tags=["coaching"])

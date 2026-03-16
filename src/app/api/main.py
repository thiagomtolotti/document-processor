from fastapi import APIRouter

from app.api.routes import default

api_router = APIRouter()

api_router.include_router(default.router)

from fastapi import APIRouter
from app.config.settings import settings
from .v1.v1_router import v1_router

api_router = APIRouter(tags=["v1"])
api_router.include_router(v1_router, prefix=settings.api.prefix)

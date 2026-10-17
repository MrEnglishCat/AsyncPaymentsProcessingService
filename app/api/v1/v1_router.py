from fastapi import APIRouter, Depends
from .payments import payments_router
from .outbox import outbox_router
from ...config.settings import settings
from ...dependencies.auth import verify_api_key

v1_router = APIRouter(tags=["v1"])
v1_router.include_router(
    payments_router,
    prefix=settings.api.v1.prefix,
    dependencies=[Depends(verify_api_key)],
)
v1_router.include_router(outbox_router, prefix=settings.api.v1.prefix)

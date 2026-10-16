from fastapi import APIRouter
from ...config.settings import settings

payments_router = APIRouter(prefix=settings.api.v1.payments)


@payments_router.get("")
def get_payments():
    return {"test": "test"}

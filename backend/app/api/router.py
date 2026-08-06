from fastapi import APIRouter

from app.api.health import router as health_router
from app.auth.router import router as auth_router
from app.products.router import router as products_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(products_router)

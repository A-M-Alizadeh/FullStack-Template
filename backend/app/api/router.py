from fastapi import APIRouter

from app.analytics.router import router as analytics_router
from app.api.health import router as health_router
from app.audit.router import router as audit_router
from app.auth.router import router as auth_router
from app.dashboard.router import router as dashboard_router
from app.passport.router import router as passport_router
from app.products.router import router as products_router
from app.users.router import router as users_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(products_router)
api_router.include_router(passport_router)
api_router.include_router(dashboard_router)
api_router.include_router(analytics_router)
api_router.include_router(audit_router)

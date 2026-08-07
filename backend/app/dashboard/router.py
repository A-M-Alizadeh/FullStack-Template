"""Dashboard HTTP routes."""

from fastapi import APIRouter

from app.auth.deps import DbSession, RequireEditorOrAdmin
from app.dashboard import service as dashboard_service
from app.schemas.dashboard import DashboardResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardResponse)
def dashboard(
    db: DbSession,
    _: RequireEditorOrAdmin,
) -> DashboardResponse:
    return dashboard_service.get_dashboard(db)

"""Analytics HTTP routes."""

from fastapi import APIRouter

from app.auth.deps import DbSession, RequireEditorOrAdmin
from app.analytics import service as analytics_service
from app.schemas.analytics import AnalyticsResponse

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("", response_model=AnalyticsResponse)
def analytics(
    db: DbSession,
    _: RequireEditorOrAdmin,
) -> AnalyticsResponse:
    return analytics_service.get_analytics(db)

"""Admin audit log list."""

from fastapi import APIRouter, Query

from app.audit import service as audit_service
from app.auth.deps import DbSession, RequireAdmin
from app.schemas.audit import AuditLogListResponse

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=AuditLogListResponse)
def list_audit_logs(
    db: DbSession,
    _: RequireAdmin,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> AuditLogListResponse:
    return audit_service.list_logs(db, skip=skip, limit=limit)

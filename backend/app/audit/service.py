"""Write and query audit logs."""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.audit.models import AuditLog
from app.schemas.audit import AuditLogListResponse, AuditLogResponse
from app.users.models import User

logger = logging.getLogger("app.audit")


def record(
    db: Session,
    *,
    actor_user_id: UUID | None,
    action: str,
    entity_type: str,
    entity_id: UUID | None = None,
    details: dict[str, Any] | None = None,
) -> None:
    """Append one audit row. Caller owns the surrounding transaction/commit."""
    db.add(
        AuditLog(
            actor_user_id=actor_user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
        )
    )
    logger.info(
        "audit action=%s entity=%s:%s actor=%s",
        action,
        entity_type,
        entity_id,
        actor_user_id,
    )


def list_logs(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 50,
) -> AuditLogListResponse:
    total = int(db.scalar(select(func.count()).select_from(AuditLog)) or 0)
    rows = list(
        db.scalars(
            select(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        ).all()
    )
    actor_ids = [r.actor_user_id for r in rows if r.actor_user_id is not None]
    emails: dict[UUID, str] = {}
    if actor_ids:
        for user in db.scalars(select(User).where(User.id.in_(actor_ids))).all():
            emails[user.id] = user.email

    items = [
        AuditLogResponse(
            id=row.id,
            actor_user_id=row.actor_user_id,
            actor_email=emails.get(row.actor_user_id) if row.actor_user_id else None,
            action=row.action,
            entity_type=row.entity_type,
            entity_id=row.entity_id,
            details=row.details,
            created_at=row.created_at,
        )
        for row in rows
    ]
    return AuditLogListResponse(items=items, total=total, skip=skip, limit=limit)

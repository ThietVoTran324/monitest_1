"""Internal admin surfaces — not linked from public UX; OpenAPI tag `admin-internal`."""

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db
from app.api.v1.deps_auth import require_admin
from app.models.monitor import EmailOutbox, EmailOutboxStatus, Monitor
from app.models.user import User
from app.workers.tasks.notify import process_email_outbox

router = APIRouter(prefix="/admin", tags=["admin-internal"])


class GrantAdminBody(BaseModel):
    email: EmailStr


class OutboxRetryBody(BaseModel):
    pass


class MonitorOutboxOverrideBody(BaseModel):
    alert_outbox_max_attempts: int | None = Field(default=None, ge=1, le=50)
    alert_outbox_backoff_seconds: str | None = Field(
        default=None,
        description="Comma-separated seconds, e.g. 60,300,900; null clears override",
    )


@router.post("/users/grant-admin")
async def grant_admin(
    body: GrantAdminBody,
    admin: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Seeded admin promotes another user. Not advertised in product UI."""
    _ = admin
    row = await session.execute(select(User).where(User.email == str(body.email).lower()))
    target = row.scalar_one_or_none()
    if target is None:
        raise HTTPException(status_code=404, detail="user_not_found")
    target.is_admin = True
    await session.commit()
    return {"id": str(target.id), "email": target.email, "is_admin": True}


@router.get("/email-outbox")
async def list_email_outbox(
    status: EmailOutboxStatus | None = None,
    limit: int = Query(50, ge=1, le=200),
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> list[dict]:
    stmt = select(EmailOutbox).order_by(EmailOutbox.created_at.desc()).limit(limit)
    if status is not None:
        stmt = stmt.where(EmailOutbox.status == status)
    rows = (await session.execute(stmt)).scalars().all()
    return [
        {
            "id": str(r.id),
            "monitor_id": str(r.monitor_id),
            "incident_id": str(r.incident_id) if r.incident_id else None,
            "event_type": r.event_type,
            "to_email": r.to_email,
            "status": r.status.value,
            "attempts": r.attempts,
            "next_attempt_at": r.next_attempt_at.isoformat() if r.next_attempt_at else None,
            "last_error": r.last_error,
            "sent_at": r.sent_at.isoformat() if r.sent_at else None,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]


@router.post("/email-outbox/{outbox_id}/retry")
async def retry_email_outbox(
    outbox_id: UUID,
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> dict:
    row = await session.get(EmailOutbox, outbox_id)
    if row is None:
        raise HTTPException(status_code=404, detail="outbox_not_found")
    row.status = EmailOutboxStatus.PENDING
    row.next_attempt_at = datetime.now(UTC)
    row.last_error = None
    await session.commit()
    process_email_outbox.delay()
    return {"id": str(row.id), "status": row.status.value}


@router.patch("/monitors/{monitor_id}/outbox-settings")
async def patch_monitor_outbox_settings(
    monitor_id: UUID,
    body: MonitorOutboxOverrideBody,
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> dict:
    monitor = await session.get(Monitor, monitor_id)
    if monitor is None or monitor.deleted_at is not None:
        raise HTTPException(status_code=404, detail="monitor_not_found")
    if "alert_outbox_max_attempts" in body.model_fields_set:
        monitor.alert_outbox_max_attempts = body.alert_outbox_max_attempts
    if "alert_outbox_backoff_seconds" in body.model_fields_set:
        monitor.alert_outbox_backoff_seconds = body.alert_outbox_backoff_seconds
    await session.commit()
    return {
        "monitor_id": str(monitor.id),
        "alert_outbox_max_attempts": monitor.alert_outbox_max_attempts,
        "alert_outbox_backoff_seconds": monitor.alert_outbox_backoff_seconds,
    }

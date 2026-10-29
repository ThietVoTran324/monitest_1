"""Email outbox: pending-in-txn enqueue + claim/send with backoff."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.monitor import (
    AlertChannel,
    AlertEvent,
    AlertEventType,
    AlertSendStatus,
    EmailOutbox,
    EmailOutboxStatus,
    Incident,
    Monitor,
)
from app.models.user import User


def parse_backoff_seconds(raw: str | None, fallback: str) -> list[int]:
    source = (raw or "").strip() or fallback
    parts: list[int] = []
    for chunk in source.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        parts.append(max(1, int(chunk)))
    return parts or [60, 300, 900]


def effective_max_attempts(monitor: Monitor) -> int:
    if monitor.alert_outbox_max_attempts is not None and monitor.alert_outbox_max_attempts > 0:
        return monitor.alert_outbox_max_attempts
    return max(1, settings.email_outbox_max_attempts)


def effective_backoff(monitor: Monitor) -> list[int]:
    return parse_backoff_seconds(
        monitor.alert_outbox_backoff_seconds,
        settings.email_outbox_backoff_seconds,
    )


def next_attempt_at_after_failure(monitor: Monitor, attempts_after: int, now: datetime) -> datetime:
    schedule = effective_backoff(monitor)
    idx = min(max(attempts_after - 1, 0), len(schedule) - 1)
    return now + timedelta(seconds=schedule[idx])


async def enqueue_alert_outbox(
    session: AsyncSession,
    *,
    monitor: Monitor,
    user: User,
    incident_id: str | None,
    event_type: str,
    now: datetime | None = None,
) -> EmailOutbox:
    ts = now or datetime.now(UTC)
    row = EmailOutbox(
        monitor_id=monitor.id,
        incident_id=incident_id,
        event_type=event_type,
        to_email=user.email,
        status=EmailOutboxStatus.PENDING,
        attempts=0,
        next_attempt_at=ts,
    )
    session.add(row)
    await session.flush()
    return row


def _build_email(monitor: Monitor, incident: Incident | None, event_enum: AlertEventType) -> tuple[str, str]:
    if event_enum == AlertEventType.INCIDENT_OPENED:
        return (
            f"[MONI] DOWN: {monitor.name}",
            (
                f"Monitor: {monitor.name}\n"
                f"URL: {monitor.url}\n"
                f"Status: DOWN\n"
                f"Checked at: {monitor.last_checked_at}\n"
                f"Error: {monitor.last_error_message or 'N/A'}\n"
            ),
        )
    if event_enum == AlertEventType.INCIDENT_RECOVERED:
        return (
            f"[MONI] RECOVERED: {monitor.name}",
            (
                f"Monitor: {monitor.name}\n"
                f"URL: {monitor.url}\n"
                f"Status: UP\n"
                f"Checked at: {monitor.last_checked_at}\n"
                f"Response time: {monitor.last_response_time_ms} ms\n"
            ),
        )
    if event_enum == AlertEventType.STILL_DOWN:
        return (
            f"[MONI] STILL DOWN: {monitor.name}",
            (
                f"Monitor: {monitor.name}\n"
                f"URL: {monitor.url}\n"
                f"Status: DOWN (ongoing incident)\n"
                f"Checked at: {monitor.last_checked_at}\n"
                f"Last error: {monitor.last_error_message or 'N/A'}\n"
                f"Reminder count: {(incident.reminder_count if incident else 0) + 1}\n"
            ),
        )
    if event_enum == AlertEventType.SSL_EXPIRY_WARNING:
        return (
            f"[MONI] SSL EXPIRY WARNING: {monitor.name}",
            (
                f"Monitor: {monitor.name}\n"
                f"URL: {monitor.url}\n"
                f"Event: SSL expiry threshold reached\n"
                f"Checked at: {monitor.last_checked_at}\n"
                f"Please review certificate renewal timeline.\n"
            ),
        )
    if event_enum == AlertEventType.DOMAIN_EXPIRY_WARNING:
        return (
            f"[MONI] DOMAIN EXPIRY WARNING: {monitor.name}",
            (
                f"Monitor: {monitor.name}\n"
                f"URL: {monitor.url}\n"
                f"Event: Domain expiry threshold reached\n"
                f"Checked at: {monitor.last_checked_at}\n"
                f"Please review domain renewal timeline.\n"
            ),
        )
    return (
        f"[MONI] STATUS UPDATE: {monitor.name}",
        f"Monitor {monitor.name} event {event_enum.value}",
    )


async def claim_due_outbox(
    session: AsyncSession,
    *,
    now: datetime | None = None,
    limit: int | None = None,
) -> list[EmailOutbox]:
    ts = now or datetime.now(UTC)
    batch = limit or settings.email_outbox_batch_size
    stmt = (
        select(EmailOutbox)
        .where(
            EmailOutbox.status == EmailOutboxStatus.PENDING,
            EmailOutbox.next_attempt_at <= ts,
        )
        .order_by(EmailOutbox.next_attempt_at)
        .limit(batch)
        .with_for_update(skip_locked=True)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def process_outbox_row(
    session: AsyncSession,
    row: EmailOutbox,
    *,
    send_email,
    now: datetime | None = None,
) -> EmailOutboxStatus:
    """Send one outbox row. `send_email(subject, to, body)` may raise."""
    ts = now or datetime.now(UTC)
    monitor = await session.get(Monitor, row.monitor_id)
    if monitor is None:
        row.status = EmailOutboxStatus.FAILED
        row.last_error = "monitor_missing"
        return row.status

    incident = await session.get(Incident, row.incident_id) if row.incident_id else None
    try:
        event_enum = AlertEventType(row.event_type)
    except ValueError:
        row.status = EmailOutboxStatus.FAILED
        row.last_error = f"unknown_event_type:{row.event_type}"
        return row.status

    subject, body = _build_email(monitor, incident, event_enum)
    row.attempts += 1
    try:
        send_email(subject, row.to_email, body)
    except Exception as exc:  # noqa: BLE001
        row.last_error = str(exc)
        max_attempts = effective_max_attempts(monitor)
        if row.attempts >= max_attempts:
            row.status = EmailOutboxStatus.FAILED
            session.add(
                AlertEvent(
                    incident_id=incident.id if incident else None,
                    monitor_id=monitor.id,
                    channel=AlertChannel.EMAIL,
                    event_type=event_enum,
                    sent_to=row.to_email,
                    sent_at=ts,
                    send_status=AlertSendStatus.FAILED,
                    error_message=row.last_error,
                )
            )
        else:
            row.status = EmailOutboxStatus.PENDING
            row.next_attempt_at = next_attempt_at_after_failure(monitor, row.attempts, ts)
        return row.status

    row.status = EmailOutboxStatus.SENT
    row.sent_at = ts
    row.last_error = None
    session.add(
        AlertEvent(
            incident_id=incident.id if incident else None,
            monitor_id=monitor.id,
            channel=AlertChannel.EMAIL,
            event_type=event_enum,
            sent_to=row.to_email,
            sent_at=ts,
            send_status=AlertSendStatus.SENT,
            error_message=None,
        )
    )
    if incident is not None:
        if event_enum == AlertEventType.INCIDENT_OPENED:
            incident.last_alert_sent_at = ts
            incident.reminder_count = 0
        elif event_enum == AlertEventType.STILL_DOWN:
            incident.last_alert_sent_at = ts
            incident.reminder_count = (incident.reminder_count or 0) + 1
    return row.status

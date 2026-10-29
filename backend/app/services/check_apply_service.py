"""Apply probe results to monitor/incident with stale + single-OPEN guards."""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.monitor import (
    CheckRun,
    CheckRunStatus,
    Incident,
    IncidentStatus,
    Monitor,
    MonitorStatus,
)

logger = logging.getLogger(__name__)


def is_probe_failure(status: CheckRunStatus) -> bool:
    return status not in {CheckRunStatus.UP, CheckRunStatus.SLOW}


def should_send_still_down_alert(
    incident: Incident,
    now: datetime,
    cooldown_minutes: int,
    reminder_minutes: int,
    max_reminders: int,
) -> bool:
    if reminder_minutes <= 0 or max_reminders <= 0:
        return False
    if (incident.reminder_count or 0) >= max_reminders:
        return False
    if now < incident.opened_at + timedelta(minutes=max(cooldown_minutes, 0)):
        return False
    if incident.last_alert_sent_at is None:
        return False
    return now >= incident.last_alert_sent_at + timedelta(minutes=reminder_minutes)


@dataclass
class AlertAction:
    monitor_id: str
    incident_id: str
    event_type: str


@dataclass
class ApplyCheckOutcome:
    applied: bool
    stale_skipped: bool
    alerts: list[AlertAction] = field(default_factory=list)


def _monitor_status_from_check(status: CheckRunStatus) -> MonitorStatus:
    if is_probe_failure(status):
        return MonitorStatus.DOWN
    if status == CheckRunStatus.SLOW:
        return MonitorStatus.SLOW
    return MonitorStatus.UP


async def _load_open_incident(session: AsyncSession, monitor_id: uuid.UUID) -> Incident | None:
    row = await session.execute(
        select(Incident)
        .where(
            Incident.monitor_id == monitor_id,
            Incident.status == IncidentStatus.OPEN,
        )
        .order_by(Incident.opened_at.desc())
        .limit(1)
    )
    return row.scalar_one_or_none()


async def apply_check_result(
    session: AsyncSession,
    monitor_id: uuid.UUID,
    check_run: CheckRun,
    *,
    alert_cooldown_minutes: int,
    alert_still_down_reminder_minutes: int,
    alert_max_reminders_per_incident: int,
) -> ApplyCheckOutcome:
    """Lock monitor, reject stale overwrite, enforce one OPEN incident.

    Caller must already have inserted ``check_run`` (flushed). Alerts are returned
    for dispatch **after** commit.
    """
    locked = await session.execute(select(Monitor).where(Monitor.id == monitor_id).with_for_update())
    monitor = locked.scalar_one()

    finished_at = check_run.finished_at
    if monitor.last_checked_at is not None and finished_at <= monitor.last_checked_at:
        logger.warning(
            "stale_check_skipped monitor_id=%s check_run_id=%s finished_at=%s last_checked_at=%s",
            monitor.id,
            check_run.id,
            finished_at.isoformat(),
            monitor.last_checked_at.isoformat(),
        )
        return ApplyCheckOutcome(applied=False, stale_skipped=True)

    status = check_run.status
    if not isinstance(status, CheckRunStatus):
        raise RuntimeError(f"monitor {monitor.id} check status is invalid")

    monitor.current_status = _monitor_status_from_check(status)
    monitor.last_checked_at = finished_at
    monitor.last_response_time_ms = check_run.response_time_ms
    monitor.last_status_code = check_run.status_code
    monitor.last_error_message = check_run.error_message
    if monitor.current_status in {MonitorStatus.UP, MonitorStatus.SLOW}:
        monitor.last_success_at = finished_at

    alerts: list[AlertAction] = []
    open_incident = await _load_open_incident(session, monitor.id)

    if monitor.current_status in {MonitorStatus.UP, MonitorStatus.SLOW}:
        if open_incident is not None:
            open_incident.status = IncidentStatus.CLOSED
            open_incident.closed_at = finished_at
            open_incident.close_reason = "Recovered by successful check"
            await session.flush()
            alerts.append(
                AlertAction(
                    monitor_id=str(monitor.id),
                    incident_id=str(open_incident.id),
                    event_type="incident_recovered",
                )
            )
        return ApplyCheckOutcome(applied=True, stale_skipped=False, alerts=alerts)

    # Failure path: open new or reuse existing OPEN.
    if open_incident is not None:
        open_incident.last_failed_check_id = check_run.id
        if should_send_still_down_alert(
            incident=open_incident,
            now=finished_at,
            cooldown_minutes=alert_cooldown_minutes,
            reminder_minutes=alert_still_down_reminder_minutes,
            max_reminders=alert_max_reminders_per_incident,
        ):
            alerts.append(
                AlertAction(
                    monitor_id=str(monitor.id),
                    incident_id=str(open_incident.id),
                    event_type="still_down",
                )
            )
        return ApplyCheckOutcome(applied=True, stale_skipped=False, alerts=alerts)

    incident = Incident(
        monitor_id=monitor.id,
        opened_at=finished_at if finished_at.tzinfo else finished_at.replace(tzinfo=UTC),
        status=IncidentStatus.OPEN,
        open_reason=check_run.error_message or (check_run.error_type or "check_failed"),
        first_failed_check_id=check_run.id,
        last_failed_check_id=check_run.id,
    )
    try:
        async with session.begin_nested():
            session.add(incident)
            await session.flush()
    except IntegrityError:
        open_incident = await _load_open_incident(session, monitor.id)
        if open_incident is None:
            raise
        open_incident.last_failed_check_id = check_run.id
        return ApplyCheckOutcome(applied=True, stale_skipped=False, alerts=[])

    alerts.append(
        AlertAction(
            monitor_id=str(monitor.id),
            incident_id=str(incident.id),
            event_type="incident_opened",
        )
    )
    return ApplyCheckOutcome(applied=True, stale_skipped=False, alerts=alerts)

"""Sprint2: stale overwrite reject + single OPEN incident."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import delete, select, text

from app.core.database import AsyncSessionLocal
from app.models.monitor import (
    CheckRun,
    CheckRunStatus,
    Incident,
    IncidentStatus,
    Monitor,
    MonitorStatus,
)
from app.models.user import User
from app.services.check_apply_service import apply_check_result, should_send_still_down_alert


async def _seed_monitor(session, *, email: str) -> Monitor:
    user_id = uuid.uuid4()
    await session.execute(delete(User).where(User.email == email))
    session.add(
        User(id=user_id, email=email, hashed_password=None, is_verified=True)
    )
    await session.flush()
    monitor = Monitor(
        user_id=user_id,
        name=f"it-apply-{email}",
        url="https://example.com",
        active_region="global",
        current_status=MonitorStatus.UP,
    )
    session.add(monitor)
    await session.flush()
    return monitor


def _check_run(
    monitor_id: uuid.UUID,
    *,
    status: CheckRunStatus,
    finished_at: datetime,
    error_message: str | None = None,
) -> CheckRun:
    return CheckRun(
        monitor_id=monitor_id,
        status=status,
        started_at=finished_at - timedelta(seconds=1),
        finished_at=finished_at,
        response_time_ms=100,
        status_code=200 if status in {CheckRunStatus.UP, CheckRunStatus.SLOW} else 500,
        error_type="http_error" if status == CheckRunStatus.HTTP_ERROR else None,
        error_message=error_message,
        probe_region="global",
        retry_count=0,
    )


@pytest.mark.asyncio
async def test_stale_check_skips_monitor_and_incident_update() -> None:
    email = "apply-stale@test.local"
    t_new = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)
    t_old = t_new - timedelta(minutes=5)

    async with AsyncSessionLocal() as session:
        monitor = await _seed_monitor(session, email=email)
        monitor.last_checked_at = t_new
        monitor.current_status = MonitorStatus.UP
        await session.flush()

        open_inc = Incident(
            monitor_id=monitor.id,
            opened_at=t_new - timedelta(hours=1),
            status=IncidentStatus.OPEN,
            open_reason="prior",
        )
        session.add(open_inc)
        await session.flush()
        incident_id = open_inc.id

        stale = _check_run(
            monitor.id,
            status=CheckRunStatus.DOWN,
            finished_at=t_old,
            error_message="late failure",
        )
        session.add(stale)
        await session.flush()

        outcome = await apply_check_result(
            session,
            monitor.id,
            stale,
            alert_cooldown_minutes=10,
            alert_still_down_reminder_minutes=30,
            alert_max_reminders_per_incident=24,
        )
        await session.commit()
        monitor_id = monitor.id
        check_id = stale.id

    assert outcome.applied is False
    assert outcome.stale_skipped is True
    assert outcome.alerts == []

    async with AsyncSessionLocal() as session:
        monitor = await session.get(Monitor, monitor_id)
        assert monitor is not None
        assert monitor.current_status == MonitorStatus.UP
        assert monitor.last_checked_at == t_new
        incident = await session.get(Incident, incident_id)
        assert incident is not None
        assert incident.status == IncidentStatus.OPEN
        saved = await session.get(CheckRun, check_id)
        assert saved is not None

        await session.execute(delete(CheckRun).where(CheckRun.monitor_id == monitor_id))
        await session.execute(delete(Incident).where(Incident.monitor_id == monitor_id))
        await session.execute(delete(Monitor).where(Monitor.id == monitor_id))
        await session.execute(delete(User).where(User.email == email))
        await session.commit()


@pytest.mark.asyncio
async def test_equal_finished_at_is_stale() -> None:
    email = "apply-equal@test.local"
    t = datetime(2026, 10, 27, 13, 0, tzinfo=UTC)

    async with AsyncSessionLocal() as session:
        monitor = await _seed_monitor(session, email=email)
        monitor.last_checked_at = t
        monitor.current_status = MonitorStatus.UP
        await session.flush()
        run = _check_run(monitor.id, status=CheckRunStatus.HTTP_ERROR, finished_at=t)
        session.add(run)
        await session.flush()
        outcome = await apply_check_result(
            session,
            monitor.id,
            run,
            alert_cooldown_minutes=10,
            alert_still_down_reminder_minutes=30,
            alert_max_reminders_per_incident=24,
        )
        await session.commit()
        monitor_id = monitor.id

    assert outcome.stale_skipped is True

    async with AsyncSessionLocal() as session:
        await session.execute(delete(CheckRun).where(CheckRun.monitor_id == monitor_id))
        await session.execute(delete(Monitor).where(Monitor.id == monitor_id))
        await session.execute(delete(User).where(User.email == email))
        await session.commit()


@pytest.mark.asyncio
async def test_open_reuse_and_recover() -> None:
    email = "apply-reuse@test.local"
    t1 = datetime(2026, 10, 27, 14, 0, tzinfo=UTC)
    t2 = t1 + timedelta(minutes=1)
    t3 = t2 + timedelta(minutes=1)

    async with AsyncSessionLocal() as session:
        monitor = await _seed_monitor(session, email=email)
        fail1 = _check_run(
            monitor.id, status=CheckRunStatus.DOWN, finished_at=t1, error_message="down1"
        )
        session.add(fail1)
        await session.flush()
        out1 = await apply_check_result(
            session,
            monitor.id,
            fail1,
            alert_cooldown_minutes=10,
            alert_still_down_reminder_minutes=30,
            alert_max_reminders_per_incident=24,
        )
        await session.commit()
        monitor_id = monitor.id

    assert out1.applied is True
    assert len(out1.alerts) == 1
    assert out1.alerts[0].event_type == "incident_opened"
    incident_id = uuid.UUID(out1.alerts[0].incident_id)

    async with AsyncSessionLocal() as session:
        fail2 = _check_run(
            monitor_id, status=CheckRunStatus.TIMEOUT, finished_at=t2, error_message="down2"
        )
        session.add(fail2)
        await session.flush()
        out2 = await apply_check_result(
            session,
            monitor_id,
            fail2,
            alert_cooldown_minutes=10,
            alert_still_down_reminder_minutes=30,
            alert_max_reminders_per_incident=24,
        )
        await session.commit()
        check2_id = fail2.id

    assert out2.applied is True
    assert out2.alerts == []  # reuse, no new incident_opened

    async with AsyncSessionLocal() as session:
        opens = (
            await session.execute(
                select(Incident).where(
                    Incident.monitor_id == monitor_id,
                    Incident.status == IncidentStatus.OPEN,
                )
            )
        ).scalars().all()
        assert len(opens) == 1
        assert opens[0].id == incident_id
        assert opens[0].last_failed_check_id == check2_id

        ok = _check_run(monitor_id, status=CheckRunStatus.UP, finished_at=t3)
        session.add(ok)
        await session.flush()
        out3 = await apply_check_result(
            session,
            monitor_id,
            ok,
            alert_cooldown_minutes=10,
            alert_still_down_reminder_minutes=30,
            alert_max_reminders_per_incident=24,
        )
        await session.commit()

    assert out3.applied is True
    assert len(out3.alerts) == 1
    assert out3.alerts[0].event_type == "incident_recovered"

    async with AsyncSessionLocal() as session:
        incident = await session.get(Incident, incident_id)
        assert incident is not None
        assert incident.status == IncidentStatus.CLOSED
        monitor = await session.get(Monitor, monitor_id)
        assert monitor is not None
        assert monitor.current_status == MonitorStatus.UP

        await session.execute(delete(CheckRun).where(CheckRun.monitor_id == monitor_id))
        await session.execute(delete(Incident).where(Incident.monitor_id == monitor_id))
        await session.execute(delete(Monitor).where(Monitor.id == monitor_id))
        await session.execute(delete(User).where(User.email == email))
        await session.commit()


@pytest.mark.asyncio
async def test_partial_unique_rejects_second_open() -> None:
    email = "apply-unique@test.local"
    t = datetime(2026, 10, 27, 15, 0, tzinfo=UTC)

    async with AsyncSessionLocal() as session:
        monitor = await _seed_monitor(session, email=email)
        session.add(
            Incident(
                monitor_id=monitor.id,
                opened_at=t,
                status=IncidentStatus.OPEN,
                open_reason="first",
            )
        )
        await session.commit()
        monitor_id = monitor.id

    async with AsyncSessionLocal() as session:
        session.add(
            Incident(
                monitor_id=monitor_id,
                opened_at=t + timedelta(seconds=1),
                status=IncidentStatus.OPEN,
                open_reason="second",
            )
        )
        with pytest.raises(Exception):
            await session.commit()
        await session.rollback()

    async with AsyncSessionLocal() as session:
        await session.execute(delete(Incident).where(Incident.monitor_id == monitor_id))
        await session.execute(delete(Monitor).where(Monitor.id == monitor_id))
        await session.execute(delete(User).where(User.email == email))
        await session.commit()


def test_should_send_still_down_alert_timeline() -> None:
    now = datetime.now(UTC)
    from types import SimpleNamespace

    incident = SimpleNamespace(
        opened_at=now - timedelta(minutes=40),
        reminder_count=0,
        last_alert_sent_at=now - timedelta(minutes=31),
    )
    assert (
        should_send_still_down_alert(
            incident=incident,  # type: ignore[arg-type]
            now=now,
            cooldown_minutes=10,
            reminder_minutes=30,
            max_reminders=24,
        )
        is True
    )


@pytest.mark.asyncio
async def test_unique_index_exists() -> None:
    async with AsyncSessionLocal() as session:
        row = await session.execute(
            text(
                """
                SELECT indexname FROM pg_indexes
                WHERE tablename = 'incidents'
                  AND indexname = 'uq_incidents_one_open_per_monitor'
                """
            )
        )
        assert row.scalar_one() == "uq_incidents_one_open_per_monitor"

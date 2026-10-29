from datetime import UTC, datetime

from app.core.database import AsyncSessionLocal, engine
from app.integrations.mail import send_email_sync
from app.models.monitor import Monitor
from app.models.user import User
from app.services.email_outbox_service import (
    enqueue_alert_outbox,
    claim_due_outbox,
    process_outbox_row,
)
from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.tasks.notify.process_email_outbox")
def process_email_outbox() -> int:
    import asyncio

    return asyncio.run(_process_email_outbox_async())


async def _process_email_outbox_async() -> int:
    processed = 0
    try:
        async with AsyncSessionLocal() as session:
            rows = await claim_due_outbox(session)
            for row in rows:
                await process_outbox_row(session, row, send_email=send_email_sync)
                processed += 1
            await session.commit()
    finally:
        await engine.dispose()
    return processed


@celery_app.task(name="app.workers.tasks.notify.send_incident_email")
def send_incident_email(monitor_id: str, incident_id: str | None, event_type: str) -> None:
    """Legacy entry: enqueue outbox row then kick processor (compat for old callers)."""
    import asyncio

    asyncio.run(_legacy_enqueue_async(monitor_id, incident_id, event_type))
    process_email_outbox.delay()


async def _legacy_enqueue_async(monitor_id: str, incident_id: str | None, event_type: str) -> None:
    try:
        async with AsyncSessionLocal() as session:
            monitor = await session.get(Monitor, monitor_id)
            if monitor is None:
                return
            user = await session.get(User, monitor.user_id)
            if user is None:
                return
            await enqueue_alert_outbox(
                session,
                monitor=monitor,
                user=user,
                incident_id=incident_id,
                event_type=event_type,
            )
            await session.commit()
    finally:
        await engine.dispose()


async def enqueue_alerts_for_monitor(
    session,
    monitor: Monitor,
    alerts: list,
) -> int:
    """Insert pending outbox rows in the same session/txn as apply. Caller commits."""
    if not alerts:
        return 0
    user = await session.get(User, monitor.user_id)
    if user is None:
        return 0
    n = 0
    for action in alerts:
        await enqueue_alert_outbox(
            session,
            monitor=monitor,
            user=user,
            incident_id=action.incident_id,
            event_type=action.event_type,
        )
        n += 1
    return n

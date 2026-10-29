from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.models.monitor import EmailOutbox, EmailOutboxStatus, Monitor
from app.services.email_outbox_service import (
    effective_max_attempts,
    next_attempt_at_after_failure,
    parse_backoff_seconds,
    process_outbox_row,
)


def test_parse_backoff_and_override():
    assert parse_backoff_seconds("60, 120", "60,300") == [60, 120]
    mon = SimpleNamespace(alert_outbox_max_attempts=3, alert_outbox_backoff_seconds="10,20")
    assert effective_max_attempts(mon) == 3
    now = datetime(2026, 1, 1, tzinfo=UTC)
    nxt = next_attempt_at_after_failure(mon, attempts_after=1, now=now)
    assert nxt == now + timedelta(seconds=10)


@pytest.mark.asyncio
async def test_process_outbox_success_writes_sent():
    monitor_id = uuid4()
    monitor = Monitor(
        id=monitor_id,
        user_id=uuid4(),
        name="m",
        url="https://example.com",
    )
    row = EmailOutbox(
        id=uuid4(),
        monitor_id=monitor_id,
        incident_id=None,
        event_type="incident_opened",
        to_email="a@b.com",
        status=EmailOutboxStatus.PENDING,
        attempts=0,
        next_attempt_at=datetime.now(UTC),
    )

    class Sess:
        def __init__(self):
            self.added = []

        async def get(self, model, pk):
            if model is Monitor and pk == monitor_id:
                return monitor
            return None

        def add(self, obj):
            self.added.append(obj)

    sent = []

    def send_email(subject, to, body):
        sent.append((subject, to, body))

    session = Sess()
    status = await process_outbox_row(session, row, send_email=send_email)
    assert status == EmailOutboxStatus.SENT
    assert row.status == EmailOutboxStatus.SENT
    assert sent and "DOWN" in sent[0][0]
    assert any(getattr(x, "send_status", None) and x.send_status.value == "sent" for x in session.added)


@pytest.mark.asyncio
async def test_process_outbox_retry_then_fail():
    monitor_id = uuid4()
    monitor = Monitor(
        id=monitor_id,
        user_id=uuid4(),
        name="m",
        url="https://example.com",
        alert_outbox_max_attempts=2,
        alert_outbox_backoff_seconds="1,2",
    )
    row = EmailOutbox(
        id=uuid4(),
        monitor_id=monitor_id,
        incident_id=None,
        event_type="incident_opened",
        to_email="a@b.com",
        status=EmailOutboxStatus.PENDING,
        attempts=0,
        next_attempt_at=datetime.now(UTC),
    )

    class Sess:
        def __init__(self):
            self.added = []

        async def get(self, model, pk):
            if model is Monitor and pk == monitor_id:
                return monitor
            return None

        def add(self, obj):
            self.added.append(obj)

    def boom(*_a, **_k):
        raise RuntimeError("smtp_down")

    session = Sess()
    status1 = await process_outbox_row(session, row, send_email=boom)
    assert status1 == EmailOutboxStatus.PENDING
    assert row.attempts == 1
    status2 = await process_outbox_row(session, row, send_email=boom)
    assert status2 == EmailOutboxStatus.FAILED
    assert row.attempts == 2

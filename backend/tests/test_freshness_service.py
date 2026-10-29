"""Sprint4: monitor freshness derive (stale vs fresh vs unknown)."""

from datetime import UTC, datetime, timedelta

from app.services.freshness_service import evaluate_monitor_freshness


def test_first_run_unknown_not_stale() -> None:
    result = evaluate_monitor_freshness(
        last_checked_at=None,
        interval_seconds=60,
        is_paused=False,
    )
    assert result.is_stale is False
    assert result.freshness == "unknown"


def test_paused_unknown_not_stale() -> None:
    now = datetime(2026, 10, 28, 12, 0, tzinfo=UTC)
    result = evaluate_monitor_freshness(
        last_checked_at=now - timedelta(hours=5),
        interval_seconds=60,
        is_paused=True,
        now=now,
    )
    assert result.is_stale is False
    assert result.freshness == "unknown"


def test_fresh_within_threshold() -> None:
    now = datetime(2026, 10, 28, 12, 0, tzinfo=UTC)
    # threshold = 60*2 + 60 = 180s
    result = evaluate_monitor_freshness(
        last_checked_at=now - timedelta(seconds=120),
        interval_seconds=60,
        is_paused=False,
        now=now,
        stale_factor=2.0,
        min_buffer_seconds=60,
    )
    assert result.is_stale is False
    assert result.freshness == "fresh"


def test_stale_beyond_factor_plus_buffer() -> None:
    now = datetime(2026, 10, 28, 12, 0, tzinfo=UTC)
    result = evaluate_monitor_freshness(
        last_checked_at=now - timedelta(seconds=181),
        interval_seconds=60,
        is_paused=False,
        now=now,
        stale_factor=2.0,
        min_buffer_seconds=60,
    )
    assert result.is_stale is True
    assert result.freshness == "stale"


def test_min_buffer_protects_short_interval_jitter() -> None:
    now = datetime(2026, 10, 28, 12, 0, tzinfo=UTC)
    # Without buffer, factor*30=60; with +60 buffer threshold=120
    result = evaluate_monitor_freshness(
        last_checked_at=now - timedelta(seconds=90),
        interval_seconds=30,
        is_paused=False,
        now=now,
        stale_factor=2.0,
        min_buffer_seconds=60,
    )
    assert result.is_stale is False
    assert result.freshness == "fresh"


def test_does_not_imply_status_down() -> None:
    """Freshness is orthogonal — helper never returns a monitor status."""
    now = datetime(2026, 10, 28, 12, 0, tzinfo=UTC)
    result = evaluate_monitor_freshness(
        last_checked_at=now - timedelta(hours=1),
        interval_seconds=60,
        is_paused=False,
        now=now,
    )
    assert result.is_stale is True
    assert not hasattr(result, "current_status")

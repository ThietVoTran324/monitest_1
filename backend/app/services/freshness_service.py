"""Monitor check freshness (stale vs fresh) — derive only, no DB mutation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal

FreshnessState = Literal["fresh", "stale", "unknown"]


@dataclass(frozen=True)
class MonitorFreshness:
    is_stale: bool
    freshness: FreshnessState


def evaluate_monitor_freshness(
    *,
    last_checked_at: datetime | None,
    interval_seconds: int,
    is_paused: bool,
    now: datetime | None = None,
    stale_factor: float = 2.0,
    min_buffer_seconds: int = 60,
) -> MonitorFreshness:
    """Return freshness without changing current_status.

    threshold = interval_seconds * stale_factor + min_buffer_seconds

    First run (``last_checked_at is None``) and paused monitors are ``unknown``
    and never ``is_stale``.
    """
    if is_paused or last_checked_at is None:
        return MonitorFreshness(is_stale=False, freshness="unknown")

    now_utc = now or datetime.now(UTC)
    if now_utc.tzinfo is None:
        now_utc = now_utc.replace(tzinfo=UTC)
    checked = last_checked_at if last_checked_at.tzinfo else last_checked_at.replace(tzinfo=UTC)

    interval = max(int(interval_seconds), 1)
    factor = max(float(stale_factor), 1.0)
    buffer = max(int(min_buffer_seconds), 0)
    threshold_seconds = interval * factor + buffer
    age = (now_utc - checked).total_seconds()
    if age > threshold_seconds:
        return MonitorFreshness(is_stale=True, freshness="stale")
    return MonitorFreshness(is_stale=False, freshness="fresh")

from datetime import datetime, timedelta, timezone

from app.core.freshness import assess_freshness


def test_fresh_data() -> None:
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    result = assess_freshness(now - timedelta(minutes=10), 90, now=now)
    assert result.status == "fresh"


def test_stale_data() -> None:
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    result = assess_freshness(now - timedelta(minutes=91), 90, now=now)
    assert result.status == "stale"

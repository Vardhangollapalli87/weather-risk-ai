from datetime import datetime, timedelta, timezone

from app.models.weather import Freshness


def assess_freshness(reported_at: datetime, max_age_minutes: int, *, now: datetime | None = None) -> Freshness:
    if reported_at.tzinfo is None:
        reported_at = reported_at.replace(tzinfo=timezone.utc)
    now = now or datetime.now(timezone.utc)
    age_minutes = max(0.0, (now - reported_at.astimezone(timezone.utc)).total_seconds() / 60)
    return Freshness(
        status="fresh" if age_minutes <= max_age_minutes else "stale",
        age_minutes=round(age_minutes, 2),
        max_age_minutes=max_age_minutes,
    )

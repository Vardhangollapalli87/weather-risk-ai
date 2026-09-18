from unittest.mock import patch

from app.core.cache import TTLCache


def test_cache_hit_and_expiration() -> None:
    cache = TTLCache[str](10)
    with patch("app.core.cache.monotonic", side_effect=[100.0, 105.0, 111.0]):
        cache.set("key", "value")
        assert cache.get("key") == "value"
        assert cache.get("key") is None

from app.core.cache import TTLCache
from app.models.weather import WeatherSnapshot
from app.providers.base import WeatherProvider


class WeatherService:
    def __init__(self, provider: WeatherProvider, cache: TTLCache[WeatherSnapshot]) -> None:
        self.provider = provider
        self.cache = cache

    async def get_weather(self, latitude: float, longitude: float) -> WeatherSnapshot:
        key = f"weather:{latitude:.4f}:{longitude:.4f}"
        return self.cache.get(key) or await self._fetch_and_cache(key, latitude, longitude)

    async def _fetch_and_cache(self, key: str, latitude: float, longitude: float) -> WeatherSnapshot:
        result = await self.provider.get_weather_snapshot(latitude, longitude)
        self.cache.set(key, result)
        return result

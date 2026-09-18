from app.core.cache import TTLCache
from app.models.location import Location
from app.providers.base import WeatherProvider


class LocationService:
    def __init__(self, provider: WeatherProvider, cache: TTLCache[list[Location]]) -> None:
        self.provider = provider
        self.cache = cache

    async def search(self, query: str) -> list[Location]:
        key = f"locations:{query.casefold()}"
        return self.cache.get(key) or await self._fetch_and_cache(key, query)

    async def _fetch_and_cache(self, key: str, query: str) -> list[Location]:
        result = await self.provider.search_locations(query)
        self.cache.set(key, result)
        return result

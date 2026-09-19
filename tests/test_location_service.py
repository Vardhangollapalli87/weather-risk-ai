import asyncio

import pytest

from app.core.cache import TTLCache
from app.models.location import ReverseLocation
from app.services.location_service import LocationService


class CountingProvider:
    def __init__(self) -> None:
        self.calls = 0

    async def reverse_geocode(self, latitude: float, longitude: float) -> ReverseLocation:
        self.calls += 1
        return ReverseLocation(name="Basar", city="Basar", state="Telangana", country="India", display_name="Basar, Telangana, India")


@pytest.mark.asyncio
async def test_reverse_cache_normalizes_nearby_coordinates() -> None:
    provider = CountingProvider()
    service = LocationService(provider, TTLCache(60), TTLCache(60))
    first = await service.reverse(18.883415, 77.920443)
    second = await service.reverse(18.883416, 77.920444)
    assert first == second
    assert provider.calls == 1


@pytest.mark.asyncio
async def test_reverse_cache_expiry_fetches_again() -> None:
    provider = CountingProvider()
    service = LocationService(provider, TTLCache(60), TTLCache(0.01))
    await service.reverse(18.8834, 77.9204)
    await asyncio.sleep(0.02)
    await service.reverse(18.8834, 77.9204)
    assert provider.calls == 2
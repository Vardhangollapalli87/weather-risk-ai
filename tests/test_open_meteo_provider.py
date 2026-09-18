from datetime import datetime, timedelta

import httpx
import pytest

from app.config import Settings
from app.core.exceptions import ProviderError, ProviderMalformedResponse
from app.providers.open_meteo import OpenMeteoProvider


def weather_payload() -> dict:
    start = datetime(2025, 12, 31)
    hours = [(start + timedelta(hours=hour)).strftime("%Y-%m-%dT%H:%M") for hour in range(49)]
    return {"timezone": "UTC", "utc_offset_seconds": 0, "generationtime_ms": 0.5, "current": {"time": hours[23], "temperature_2m": 25.0, "relative_humidity_2m": 70, "pressure_msl": 1010.0, "wind_speed_10m": 12.0, "cloud_cover": 50, "precipitation": 1.0, "weather_code": 61}, "hourly": {"time": hours, "temperature_2m": [25.0] * 49, "relative_humidity_2m": [70] * 49, "pressure_msl": [1010.0] * 49, "wind_speed_10m": [12.0] * 49, "cloud_cover": [50] * 49, "precipitation": [1.0] * 49, "precipitation_probability": [60] * 49, "weather_code": [61] * 49}}


def mock_client(payload: dict, status_code: int = 200) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.MockTransport(lambda _: httpx.Response(status_code, json=payload)))


@pytest.mark.asyncio
async def test_location_response_is_normalized() -> None:
    client = mock_client({"results": [{"id": 1, "name": "Hyderabad", "country": "India", "admin1": "Telangana", "latitude": 17.385, "longitude": 78.4867, "timezone": "Asia/Kolkata"}]})
    provider = OpenMeteoProvider(Settings(), client)
    locations = await provider.search_locations("Hyderabad")
    await client.aclose()
    assert locations[0].name == "Hyderabad"
    assert locations[0].admin1 == "Telangana"


@pytest.mark.asyncio
async def test_snapshot_parses_hourly_and_rainfall() -> None:
    client = mock_client(weather_payload())
    provider = OpenMeteoProvider(Settings(weather_max_staleness_minutes=9_999_999), client)
    snapshot = await provider.get_weather_snapshot(17.38, 78.48)
    await client.aclose()
    assert snapshot.current.temperature_c == 25.0
    assert len(snapshot.hourly_forecast) == 24
    assert snapshot.rainfall.recent_24h_mm == 24.0
    assert snapshot.rainfall.forecast_next_24h_mm == 24.0
    assert snapshot.freshness.status == "fresh"


@pytest.mark.asyncio
async def test_malformed_weather_is_rejected() -> None:
    client = mock_client({"current": {}, "hourly": {}})
    provider = OpenMeteoProvider(Settings(), client)
    with pytest.raises(ProviderMalformedResponse):
        await provider.get_weather_snapshot(0, 0)
    await client.aclose()


@pytest.mark.asyncio
async def test_timeout_is_provider_error() -> None:
    async def failing(_: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timeout")
    client = httpx.AsyncClient(transport=httpx.MockTransport(failing))
    provider = OpenMeteoProvider(Settings(weather_max_retries=0), client)
    with pytest.raises(ProviderError):
        await provider.search_locations("Hyderabad")
    await client.aclose()


@pytest.mark.asyncio
async def test_http_failure_is_provider_error() -> None:
    client = mock_client({"reason": "bad request"}, 400)
    provider = OpenMeteoProvider(Settings(), client)
    with pytest.raises(ProviderError) as error:
        await provider.search_locations("Hyderabad")
    await client.aclose()
    assert error.value.retryable is False

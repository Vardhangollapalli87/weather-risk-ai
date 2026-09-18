from fastapi.testclient import TestClient

from app.config import Settings
from app.core.cache import TTLCache
from app.core.exceptions import ProviderError
from app.main import app
from app.models.location import Location
from app.providers.open_meteo import OpenMeteoProvider
from app.services.location_service import LocationService
from app.services.weather_service import WeatherService
from tests.test_open_meteo_provider import mock_client, weather_payload


def setup_services() -> None:
    provider = OpenMeteoProvider(Settings(weather_max_staleness_minutes=9_999_999), mock_client(weather_payload()))
    app.state.location_service = LocationService(provider, TTLCache(60))
    app.state.weather_service = WeatherService(provider, TTLCache(60))


def test_health() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_weather_response_schema() -> None:
    with TestClient(app) as client:
        setup_services()
        response = client.get("/weather", params={"latitude": 17.385, "longitude": 78.4867})
    assert response.status_code == 200
    body = response.json()
    assert body["rainfall"]["recent_24h_mm"] == 24.0
    assert len(body["hourly_forecast"]) == 24


def test_invalid_coordinates_are_structured_errors() -> None:
    with TestClient(app) as client:
        response = client.get("/weather", params={"latitude": 100, "longitude": 78})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_empty_and_long_location_query_are_rejected() -> None:
    with TestClient(app) as client:
        empty = client.get("/locations", params={"query": ""})
        long = client.get("/locations", params={"query": "a" * 101})
    assert empty.status_code == 422
    assert long.status_code == 422


def test_provider_failure_is_structured() -> None:
    class BrokenProvider:
        async def get_weather_snapshot(self, latitude: float, longitude: float):
            raise ProviderError("Weather provider request timed out")
        async def search_locations(self, query: str) -> list[Location]:
            raise ProviderError("Weather provider request timed out")
    with TestClient(app) as client:
        app.state.weather_service = WeatherService(BrokenProvider(), TTLCache(60))
        response = client.get("/weather", params={"latitude": 1, "longitude": 1})
    assert response.status_code == 503
    assert response.json()["error"]["retryable"] is True

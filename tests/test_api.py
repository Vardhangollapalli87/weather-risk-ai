from fastapi.testclient import TestClient

from app.config import Settings
from app.core.cache import TTLCache
from app.core.exceptions import LocationProviderError, ProviderError
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


def test_reverse_invalid_coordinates_are_structured_errors() -> None:
    with TestClient(app) as client:
        invalid_latitude = client.get("/locations/reverse", params={"latitude": 90.01, "longitude": 78})
        invalid_longitude = client.get("/locations/reverse", params={"latitude": 18, "longitude": 180.01})
    assert invalid_latitude.status_code == 422
    assert invalid_longitude.status_code == 422
    assert invalid_latitude.json()["error"]["code"] == "VALIDATION_ERROR"


def test_reverse_provider_failure_has_location_error_contract() -> None:
    class BrokenProvider:
        async def reverse_geocode(self, latitude: float, longitude: float):
            raise LocationProviderError("Reverse geocoding provider request failed")

    with TestClient(app) as client:
        app.state.location_service = LocationService(BrokenProvider(), TTLCache(60))
        response = client.get("/locations/reverse", params={"latitude": 18, "longitude": 78})
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "LOCATION_PROVIDER_ERROR"
    assert response.json()["error"]["retryable"] is True
    assert response.json()["error"]["message"] == "Reverse geocoding provider request failed"


def test_analysis_does_not_depend_on_reverse_geocoding() -> None:
    from app.agent.graph import WeatherRiskAgent
    from tests.test_agent_graph import FakeAnalysisService, sample_weather

    class BrokenReverseProvider:
        async def reverse_geocode(self, latitude: float, longitude: float):
            raise LocationProviderError("Reverse geocoding provider request failed")

    with TestClient(app) as client:
        app.state.location_service = LocationService(BrokenReverseProvider(), TTLCache(60))
        app.state.weather_risk_agent = WeatherRiskAgent(FakeAnalysisService(sample_weather()))
        response = client.post("/analysis", json={"latitude": 18, "longitude": 78, "location_name": "Current location"})
    assert response.status_code == 200


def test_empty_and_long_location_query_are_rejected() -> None:
    with TestClient(app) as client:
        empty = client.get("/locations", params={"query": ""})
        long = client.get("/locations", params={"query": "a" * 101})
        whitespace = client.get("/locations", params={"query": "   "})
    assert empty.status_code == 422
    assert long.status_code == 422
    assert whitespace.status_code == 422
    assert whitespace.json()["error"]["code"] == "VALIDATION_ERROR"


def test_coordinate_boundaries_and_cors_post_preflight() -> None:
    with TestClient(app) as client:
        setup_services()
        minimum = client.get("/weather", params={"latitude": -90, "longitude": -180})
        maximum = client.get("/weather", params={"latitude": 90, "longitude": 180})
        invalid = client.get("/weather", params={"latitude": 90.01, "longitude": 180.01})
        preflight = client.options("/analysis", headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "content-type"})
    assert minimum.status_code != 422
    assert maximum.status_code != 422
    assert invalid.status_code == 422
    assert preflight.status_code == 200
    assert "POST" in preflight.headers["access-control-allow-methods"]


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

import pytest

from app.agent.graph import WeatherRiskAgent
from app.models.analysis import AnalysisResponse, Explanation
from app.ml.inference import MLPrediction
from app.risk.engine import assess_risk
from tests.test_open_meteo_provider import mock_client, weather_payload
from app.config import Settings
from app.providers.open_meteo import OpenMeteoProvider


class FakeWeatherService:
    def __init__(self, weather):
        self.weather = weather

    async def get_weather(self, latitude: float, longitude: float):
        return self.weather


class FakeAnalysisService:
    def __init__(self, weather):
        self.weather_service = FakeWeatherService(weather)

    def analyze_weather(self, weather, location_name):
        prediction = MLPrediction(probability=0.8, classification=True, target="next_24h_precipitation_gte_20mm", model_version="test-v1", feature_schema_version="v1")
        return AnalysisResponse(location_name=location_name, weather=weather, ml_prediction=prediction, risk=assess_risk(0.8, weather.rainfall.forecast_next_24h_mm, 60, weather.rainfall.recent_24h_mm), status="fresh")


def sample_weather():
    provider = OpenMeteoProvider(Settings(weather_max_staleness_minutes=9_999_999), mock_client(weather_payload()))
    return provider._parse_snapshot(weather_payload(), 17.385, 78.4867)


class BrokenProvider:
    def generate(self, evidence):
        raise TimeoutError("provider timed out")


class UnsafeProvider:
    def generate(self, evidence):
        return Explanation(summary="High flood risk with 999 mm rain.", why_this_risk=[], key_factors=[], what_to_watch=[], disclaimer="Official warning.", source="mock")


class ValidProvider:
    def generate(self, evidence):
        return Explanation(summary=f"{evidence.risk_level} significant-rainfall risk.", why_this_risk=["The deterministic assessment uses verified weather and model evidence."], key_factors=evidence.factors[:2], what_to_watch=["Monitor changes in the hourly forecast."], disclaimer="This is decision support, not an official warning or flood prediction.", source="mock")


@pytest.mark.asyncio
async def test_graph_uses_template_when_no_provider() -> None:
    result = await WeatherRiskAgent(FakeAnalysisService(sample_weather())).invoke(17.385, 78.4867, "Hyderabad")
    assert result.explanation is not None
    assert result.explanation.source == "template"
    assert result.explanation.summary.startswith(result.risk.level)


@pytest.mark.asyncio
async def test_provider_timeout_falls_back_to_template() -> None:
    result = await WeatherRiskAgent(FakeAnalysisService(sample_weather()), BrokenProvider()).invoke(17.385, 78.4867)
    assert result.explanation is not None
    assert result.explanation.source == "template"


@pytest.mark.asyncio
async def test_valid_provider_explanation_is_returned_without_altering_analysis() -> None:
    result = await WeatherRiskAgent(FakeAnalysisService(sample_weather()), ValidProvider()).invoke(17.385, 78.4867)
    assert result.explanation is not None
    assert result.explanation.source == "mock"
    assert result.ml_prediction.probability == 0.8
    assert result.risk.score == assess_risk(0.8, 24, 60, 24).score


@pytest.mark.asyncio
async def test_unsafe_provider_claims_fall_back_to_template() -> None:
    result = await WeatherRiskAgent(FakeAnalysisService(sample_weather()), UnsafeProvider()).invoke(17.385, 78.4867)
    assert result.explanation is not None
    assert result.explanation.source == "template"
    assert "999" not in result.explanation.summary

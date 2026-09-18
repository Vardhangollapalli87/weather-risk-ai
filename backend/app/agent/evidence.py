from pydantic import BaseModel

from app.models.analysis import AnalysisResponse


class Evidence(BaseModel):
    location_name: str
    latitude: float
    longitude: float
    current_temperature_c: float | None
    recent_24h_rain_mm: float
    forecast_24h_rain_mm: float
    max_hourly_precipitation_probability_percent: float
    ml_probability: float
    ml_target: str
    model_version: str
    risk_score: float
    risk_level: str
    factors: list[str]
    freshness_status: str
    retrieved_at: str


def build_evidence(result: AnalysisResponse) -> Evidence:
    probabilities = [hour.precipitation_probability_percent for hour in result.weather.hourly_forecast]
    return Evidence(location_name=result.location_name or result.weather.location.name, latitude=result.weather.location.latitude, longitude=result.weather.location.longitude, current_temperature_c=result.weather.current.temperature_c, recent_24h_rain_mm=result.weather.rainfall.recent_24h_mm, forecast_24h_rain_mm=result.weather.rainfall.forecast_next_24h_mm, max_hourly_precipitation_probability_percent=max(float(value) for value in probabilities if value is not None), ml_probability=result.ml_prediction.probability, ml_target=result.ml_prediction.target, model_version=result.ml_prediction.model_version, risk_score=result.risk.score, risk_level=result.risk.level, factors=[factor.name for factor in result.risk.factors], freshness_status=result.status, retrieved_at=result.weather.retrieved_at.isoformat())

from pydantic import BaseModel, Field


class RiskFactor(BaseModel):
    name: str
    value: float
    indicator: float
    threshold: str


class RiskAssessment(BaseModel):
    score: float = Field(ge=0, le=100)
    level: str
    ml_probability_percent: float
    forecast_next_24h_mm: float
    max_hourly_precipitation_probability_percent: float
    recent_24h_mm: float
    indicators: dict[str, float]
    triggered_thresholds: dict[str, str]
    factors: list[RiskFactor]
    calculation_version: str = "risk-v1"


def rainfall_indicator(value: float) -> tuple[float, str]:
    if value < 2: return 0, "<2 mm"
    if value < 10: return 20, "2–<10 mm"
    if value < 20: return 50, "10–<20 mm"
    if value < 40: return 80, "20–<40 mm"
    return 100, "≥40 mm"


def assess_risk(ml_probability: float, forecast_next_24h_mm: float, max_hourly_pop: float, recent_24h_mm: float) -> RiskAssessment:
    if not 0 <= ml_probability <= 1: raise ValueError("ML probability must be between 0 and 1")
    if not 0 <= max_hourly_pop <= 100: raise ValueError("Maximum hourly precipitation probability must be between 0 and 100")
    forecast_indicator, forecast_band = rainfall_indicator(forecast_next_24h_mm)
    recent_indicator, recent_band = rainfall_indicator(recent_24h_mm)
    ml_percent = ml_probability * 100
    score = round(0.45 * ml_percent + 0.30 * forecast_indicator + 0.15 * max_hourly_pop + 0.10 * recent_indicator, 2)
    level = "Low" if score < 35 else "Moderate" if score < 65 else "High"
    factors = [RiskFactor(name="ML probability of next-24h rainfall ≥20 mm", value=round(ml_percent, 2), indicator=round(ml_percent, 2), threshold="model probability"), RiskFactor(name="Forecast next-24h precipitation", value=forecast_next_24h_mm, indicator=forecast_indicator, threshold=forecast_band), RiskFactor(name="Maximum hourly precipitation probability", value=max_hourly_pop, indicator=max_hourly_pop, threshold="0–100% forecast probability"), RiskFactor(name="Recent 24h precipitation", value=recent_24h_mm, indicator=recent_indicator, threshold=recent_band)]
    return RiskAssessment(score=score, level=level, ml_probability_percent=round(ml_percent, 2), forecast_next_24h_mm=forecast_next_24h_mm, max_hourly_precipitation_probability_percent=max_hourly_pop, recent_24h_mm=recent_24h_mm, indicators={"ml_probability": round(ml_percent, 2), "forecast_24h": forecast_indicator, "max_hourly_pop": max_hourly_pop, "recent_24h": recent_indicator}, triggered_thresholds={"forecast_24h": forecast_band, "recent_24h": recent_band, "risk_level": "<35 Low; 35–<65 Moderate; ≥65 High"}, factors=sorted(factors, key=lambda factor: factor.indicator, reverse=True))

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.location import Location


class CurrentConditions(BaseModel):
    time: datetime
    temperature_c: float | None = None
    relative_humidity_percent: float | None = None
    pressure_msl_hpa: float | None = None
    wind_speed_kmh: float | None = None
    cloud_cover_percent: float | None = None
    precipitation_mm: float | None = None
    weather_code: int | None = None


class HourlyWeather(BaseModel):
    time: datetime
    temperature_c: float | None = None
    relative_humidity_percent: float | None = None
    pressure_msl_hpa: float | None = None
    wind_speed_kmh: float | None = None
    cloud_cover_percent: float | None = None
    precipitation_mm: float | None = None
    precipitation_probability_percent: float | None = Field(default=None, ge=0, le=100)
    weather_code: int | None = None


class RainfallSummary(BaseModel):
    recent_24h_mm: float = Field(ge=0)
    forecast_next_24h_mm: float = Field(ge=0)


class ProviderMetadata(BaseModel):
    name: str
    model: str | None = None
    generation_time_ms: float | None = None


class Freshness(BaseModel):
    status: str
    age_minutes: float = Field(ge=0)
    max_age_minutes: int


class WeatherSnapshot(BaseModel):
    location: Location
    timezone: str
    current: CurrentConditions
    recent_hourly: list[HourlyWeather]
    hourly_forecast: list[HourlyWeather]
    rainfall: RainfallSummary
    provider: ProviderMetadata
    retrieved_at: datetime
    freshness: Freshness

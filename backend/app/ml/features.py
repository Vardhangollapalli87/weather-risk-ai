import math

import pandas as pd

from app.models.weather import WeatherSnapshot

FEATURE_COLUMNS = ["temperature_c", "relative_humidity_percent", "pressure_msl_hpa", "wind_speed_kmh", "cloud_cover_percent", "precipitation_mm", "previous_hour_precipitation_mm", "rolling_6h_precipitation_mm", "rolling_24h_precipitation_mm", "hour", "month", "hour_sin", "hour_cos"]
REQUIRED_SOURCE_COLUMNS = ["time", "temperature_c", "relative_humidity_percent", "pressure_msl_hpa", "wind_speed_kmh", "cloud_cover_percent", "precipitation_mm"]


def build_training_features(frame: pd.DataFrame, rainfall_threshold_mm: float = 20.0) -> pd.DataFrame:
    """Create features available at t and target made only from t+1 through t+24."""
    missing = set(REQUIRED_SOURCE_COLUMNS) - set(frame.columns)
    if missing:
        raise ValueError(f"Missing source columns: {sorted(missing)}")
    data = frame.copy().sort_values("time").reset_index(drop=True)
    data["time"] = pd.to_datetime(data["time"], utc=True)
    if not data["time"].is_monotonic_increasing or data["time"].duplicated().any():
        raise ValueError("Timestamps must be unique and chronological")
    precipitation = data["precipitation_mm"].astype(float)
    data["previous_hour_precipitation_mm"] = precipitation.shift(1)
    data["rolling_6h_precipitation_mm"] = precipitation.rolling(6, min_periods=6).sum()
    data["rolling_24h_precipitation_mm"] = precipitation.rolling(24, min_periods=24).sum()
    data["future_24h_precipitation_mm"] = sum(precipitation.shift(-offset) for offset in range(1, 25))
    data["significant_rain_next_24h"] = (data["future_24h_precipitation_mm"] >= rainfall_threshold_mm).astype("Int64")
    data.loc[data["future_24h_precipitation_mm"].isna(), "significant_rain_next_24h"] = pd.NA
    data["hour"] = data["time"].dt.hour
    data["month"] = data["time"].dt.month
    data["hour_sin"] = data["hour"].map(lambda hour: math.sin(2 * math.pi * hour / 24))
    data["hour_cos"] = data["hour"].map(lambda hour: math.cos(2 * math.pi * hour / 24))
    return data


def build_runtime_features(snapshot: WeatherSnapshot) -> pd.DataFrame:
    recent = snapshot.recent_hourly
    if len(recent) < 24:
        raise ValueError("At least 24 recent hourly observations are required for ML inference")
    values = [hour.precipitation_mm for hour in recent]
    if any(value is None for value in values):
        raise ValueError("Recent precipitation is required for ML inference")
    current = snapshot.current
    sources = [current.temperature_c, current.relative_humidity_percent, current.pressure_msl_hpa, current.wind_speed_kmh, current.cloud_cover_percent, current.precipitation_mm]
    if any(value is None for value in sources):
        raise ValueError("Current meteorological fields are required for ML inference")
    hour = current.time.hour
    row = {"temperature_c": current.temperature_c, "relative_humidity_percent": current.relative_humidity_percent, "pressure_msl_hpa": current.pressure_msl_hpa, "wind_speed_kmh": current.wind_speed_kmh, "cloud_cover_percent": current.cloud_cover_percent, "precipitation_mm": current.precipitation_mm, "previous_hour_precipitation_mm": values[-2], "rolling_6h_precipitation_mm": sum(values[-6:]), "rolling_24h_precipitation_mm": sum(values[-24:]), "hour": hour, "month": current.time.month, "hour_sin": math.sin(2 * math.pi * hour / 24), "hour_cos": math.cos(2 * math.pi * hour / 24)}
    return pd.DataFrame([row], columns=FEATURE_COLUMNS)

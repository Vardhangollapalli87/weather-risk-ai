import pandas as pd

from app.ml.features import FEATURE_COLUMNS, build_training_features


def source_frame(hours: int = 50) -> pd.DataFrame:
    return pd.DataFrame({"time": pd.date_range("2024-01-01", periods=hours, freq="h", tz="UTC"), "temperature_c": [20.0] * hours, "relative_humidity_percent": [60.0] * hours, "pressure_msl_hpa": [1010.0] * hours, "wind_speed_kmh": [10.0] * hours, "cloud_cover_percent": [50.0] * hours, "precipitation_mm": list(range(hours))})


def test_target_is_strictly_next_24_hours() -> None:
    features = build_training_features(source_frame())
    assert features.loc[0, "future_24h_precipitation_mm"] == sum(range(1, 25))
    assert features.loc[0, "significant_rain_next_24h"] == 1


def test_current_and_past_features_do_not_change_when_future_changes() -> None:
    original = source_frame()
    changed = original.copy()
    changed.loc[30:, "precipitation_mm"] = 999.0
    first = build_training_features(original).loc[24, FEATURE_COLUMNS]
    second = build_training_features(changed).loc[24, FEATURE_COLUMNS]
    pd.testing.assert_series_equal(first, second)


def test_rolling_features_use_current_and_past_only() -> None:
    result = build_training_features(source_frame())
    assert result.loc[24, "previous_hour_precipitation_mm"] == 23
    assert result.loc[24, "rolling_6h_precipitation_mm"] == sum(range(19, 25))
    assert result.loc[24, "rolling_24h_precipitation_mm"] == sum(range(1, 25))

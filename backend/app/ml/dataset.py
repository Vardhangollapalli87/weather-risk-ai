from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from app.ml.features import FEATURE_COLUMNS, REQUIRED_SOURCE_COLUMNS, build_training_features


@dataclass(frozen=True)
class DatasetReport:
    retrieved_rows: int
    invalid_rows: int
    missing_rows: int
    removed_rows: int
    final_rows: int
    positive_samples: int
    negative_samples: int


def normalize_historical(payload: dict, location_name: str) -> pd.DataFrame:
    hourly = payload.get("hourly")
    if not isinstance(hourly, dict):
        raise ValueError("Historical provider response lacks hourly data")
    field_map = {"temperature_2m": "temperature_c", "relative_humidity_2m": "relative_humidity_percent", "pressure_msl": "pressure_msl_hpa", "wind_speed_10m": "wind_speed_kmh", "cloud_cover": "cloud_cover_percent", "precipitation": "precipitation_mm"}
    try:
        data = {"time": hourly["time"], **{target: hourly[source] for source, target in field_map.items()}}
    except KeyError as exc:
        raise ValueError(f"Historical provider response missing {exc.args[0]}") from exc
    frame = pd.DataFrame(data)
    frame["location"] = location_name
    frame["time"] = pd.to_datetime(frame["time"], utc=True, errors="coerce")
    return frame


def prepare_dataset(frames: list[pd.DataFrame], rainfall_threshold_mm: float = 20.0) -> tuple[pd.DataFrame, DatasetReport]:
    prepared: list[pd.DataFrame] = []
    retrieved = invalid = missing = removed = 0
    for frame in frames:
        retrieved += len(frame)
        invalid_mask = frame["time"].isna() | frame["time"].duplicated()
        invalid += int(invalid_mask.sum())
        valid = frame.loc[~invalid_mask].sort_values("time").copy()
        missing_mask = valid[REQUIRED_SOURCE_COLUMNS].isna().any(axis=1)
        missing += int(missing_mask.sum())
        valid = valid.loc[~missing_mask]
        featured = build_training_features(valid, rainfall_threshold_mm)
        usable = featured.dropna(subset=FEATURE_COLUMNS + ["significant_rain_next_24h"])
        removed += len(valid) - len(usable)
        prepared.append(usable)
    dataset = pd.concat(prepared, ignore_index=True).sort_values("time").reset_index(drop=True)
    dataset["significant_rain_next_24h"] = dataset["significant_rain_next_24h"].astype(int)
    positives = int(dataset["significant_rain_next_24h"].sum())
    return dataset, DatasetReport(retrieved, invalid, missing, removed, len(dataset), positives, len(dataset) - positives)


def save_dataset(dataset: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(path, index=False)

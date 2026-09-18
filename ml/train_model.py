"""Run locally: .venv\\Scripts\\python.exe ml/train_model.py"""
import asyncio
from datetime import date
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))

from app.config import Settings
from app.ml.dataset import normalize_historical, prepare_dataset, save_dataset
from app.ml.training import train_and_persist
from app.providers.open_meteo import OpenMeteoProvider

LOCATIONS = [("Hyderabad, India", 17.385, 78.4867), ("Mumbai, India", 19.076, 72.8777), ("Bengaluru, India", 12.9716, 77.5946)]
START_DATE = date(2022, 1, 1)
END_DATE = date(2024, 12, 31)


async def main() -> None:
    provider = OpenMeteoProvider(Settings())
    frames = []
    for name, latitude, longitude in LOCATIONS:
        payload = await provider.get_historical_hourly(latitude, longitude, START_DATE, END_DATE)
        frames.append(normalize_historical(payload, name))
    dataset, report = prepare_dataset(frames)
    save_dataset(dataset, Path("data/processed/phase2_dataset.csv"))
    metadata = train_and_persist(dataset, Path("models/weather_risk_model.joblib"))
    Path("models/weather_risk_model.metadata.json").write_text(__import__("json").dumps({"dataset_report": report.__dict__, **metadata}, indent=2), encoding="utf-8")
    print({"dataset_report": report.__dict__, "selected_model": "calibrated model selected from validation comparison", "test_metrics": metadata["final_test_metrics"]})


if __name__ == "__main__":
    asyncio.run(main())

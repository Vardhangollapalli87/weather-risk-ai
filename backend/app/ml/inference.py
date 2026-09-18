from pathlib import Path

import joblib
from pydantic import BaseModel

from app.ml.features import FEATURE_COLUMNS, build_runtime_features
from app.models.weather import WeatherSnapshot
from app.core.exceptions import MLArtifactError


class MLPrediction(BaseModel):
    probability: float
    classification: bool
    target: str
    model_version: str
    feature_schema_version: str
    status: str = "available"


class MLService:
    def __init__(self, artifact_path: Path) -> None:
        self.artifact_path = artifact_path
        self._artifact: dict | None = None

    def predict(self, snapshot: WeatherSnapshot) -> MLPrediction:
        if not self.artifact_path.exists():
            raise FileNotFoundError("ML model artifact is unavailable. Train Phase 2 model first.")
        features = build_runtime_features(snapshot)
        try:
            self._artifact = self._artifact or joblib.load(self.artifact_path)
            metadata = self._artifact["metadata"]
            if metadata["feature_names"] != FEATURE_COLUMNS:
                raise MLArtifactError("Model feature schema does not match runtime schema")
            probability = float(self._artifact["model"].predict_proba(features)[0, 1])
        except MLArtifactError:
            raise
        except (KeyError, TypeError, AttributeError, OSError, EOFError, ValueError) as exc:
            raise MLArtifactError("ML model artifact is invalid or cannot produce a prediction") from exc
        if not 0 <= probability <= 1:
            raise MLArtifactError("ML model produced an invalid probability")
        return MLPrediction(probability=round(probability, 5), classification=probability >= metadata["classification_threshold"], target=metadata["target"], model_version=metadata["model_version"], feature_schema_version=metadata["feature_schema_version"])

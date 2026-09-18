from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score

from app.ml.features import FEATURE_COLUMNS


@dataclass(frozen=True)
class SplitData:
    train: pd.DataFrame
    validation: pd.DataFrame
    test: pd.DataFrame


def chronological_split(data: pd.DataFrame) -> SplitData:
    ordered = data.sort_values("time").reset_index(drop=True)
    train_end, validation_end = int(len(ordered) * 0.70), int(len(ordered) * 0.85)
    return SplitData(ordered.iloc[:train_end], ordered.iloc[train_end:validation_end], ordered.iloc[validation_end:])


def metrics(y_true: pd.Series, probabilities: np.ndarray, threshold: float) -> dict[str, Any]:
    predictions = probabilities >= threshold
    return {"pr_auc": round(float(average_precision_score(y_true, probabilities)), 5), "roc_auc": round(float(roc_auc_score(y_true, probabilities)), 5), "recall": round(float(recall_score(y_true, predictions, zero_division=0)), 5), "precision": round(float(precision_score(y_true, predictions, zero_division=0)), 5), "f1": round(float(f1_score(y_true, predictions, zero_division=0)), 5), "brier_score": round(float(brier_score_loss(y_true, probabilities)), 5), "confusion_matrix": confusion_matrix(y_true, predictions).tolist()}


def select_threshold(y_true: pd.Series, probabilities: np.ndarray) -> float:
    candidates = np.arange(0.20, 0.81, 0.05)
    # F1 selection occurs only on validation data; recall breaks ties.
    return float(max(candidates, key=lambda t: (f1_score(y_true, probabilities >= t, zero_division=0), recall_score(y_true, probabilities >= t, zero_division=0))))


def train_and_persist(dataset: pd.DataFrame, artifact_path: Path) -> dict[str, Any]:
    split = chronological_split(dataset)
    target = "significant_rain_next_24h"
    x_train, y_train = split.train[FEATURE_COLUMNS], split.train[target]
    x_validation, y_validation = split.validation[FEATURE_COLUMNS], split.validation[target]
    baseline = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)
    candidate = RandomForestClassifier(n_estimators=200, min_samples_leaf=5, class_weight="balanced", random_state=42, n_jobs=-1)
    models = {"logistic_regression": baseline, "random_forest": candidate}
    comparison: dict[str, dict[str, Any]] = {}
    fitted: dict[str, Any] = {}
    for name, model in models.items():
        # Calibrate inside training data only, before validation-based model and threshold selection.
        calibrated = CalibratedClassifierCV(model, method="sigmoid", cv=3)
        calibrated.fit(x_train, y_train)
        probs = calibrated.predict_proba(x_validation)[:, 1]
        threshold = select_threshold(y_validation, probs)
        comparison[name] = {"threshold": threshold, **metrics(y_validation, probs, threshold)}
        fitted[name] = calibrated
    selected_name = max(comparison, key=lambda name: (comparison[name]["pr_auc"], comparison[name]["recall"]))
    threshold = comparison[selected_name]["threshold"]
    # Calibration uses only train+validation after model/threshold selection; held-out test remains untouched.
    final_base = RandomForestClassifier(n_estimators=200, min_samples_leaf=5, class_weight="balanced", random_state=42, n_jobs=-1) if selected_name == "random_forest" else LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)
    final_model = CalibratedClassifierCV(final_base, method="sigmoid", cv=3)
    combined = pd.concat([split.train, split.validation])
    final_model.fit(combined[FEATURE_COLUMNS], combined[target])
    test_probabilities = final_model.predict_proba(split.test[FEATURE_COLUMNS])[:, 1]
    final_test_metrics = metrics(split.test[target], test_probabilities, threshold)
    metadata = {"model_version": "phase2-v1", "feature_schema_version": "v1", "target": "next_24h_precipitation_gte_20mm", "rainfall_threshold_mm": 20.0, "classification_threshold": threshold, "feature_names": FEATURE_COLUMNS, "data_source": "Open-Meteo historical/reanalysis weather data, not station observations", "created_at": datetime.now(timezone.utc).isoformat(), "splits": {name: {"rows": len(part), "start": part["time"].min().isoformat(), "end": part["time"].max().isoformat()} for name, part in [("train", split.train), ("validation", split.validation), ("test", split.test)]}, "validation_comparison": comparison, "final_test_metrics": final_test_metrics}
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": final_model, "metadata": metadata}, artifact_path)
    return metadata

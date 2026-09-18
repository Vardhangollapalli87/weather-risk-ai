from pathlib import Path

import joblib
import pytest

from app.core.exceptions import MLArtifactError
from app.ml.inference import MLService
from tests.test_agent_graph import sample_weather


def test_invalid_model_schema_is_rejected(tmp_path: Path) -> None:
    artifact = tmp_path / "invalid.joblib"
    joblib.dump({"model": object(), "metadata": {"feature_names": ["wrong"]}}, artifact)
    with pytest.raises(MLArtifactError):
        MLService(artifact).predict(sample_weather())

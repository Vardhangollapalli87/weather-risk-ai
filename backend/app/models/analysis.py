from pydantic import BaseModel, Field

from app.ml.inference import MLPrediction
from app.models.weather import WeatherSnapshot
from app.risk.engine import RiskAssessment


class Explanation(BaseModel):
    summary: str
    why_this_risk: list[str]
    key_factors: list[str]
    what_to_watch: list[str]
    disclaimer: str
    source: str


class AnalysisRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    location_name: str | None = Field(default=None, max_length=100)


class AnalysisResponse(BaseModel):
    location_name: str | None = None
    weather: WeatherSnapshot
    ml_prediction: MLPrediction
    risk: RiskAssessment
    explanation: Explanation | None = None
    status: str

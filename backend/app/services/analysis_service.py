from app.core.exceptions import MLArtifactError, MLUnavailableError, RuntimeDataError
from app.ml.inference import MLService
from app.models.analysis import AnalysisResponse
from app.risk.engine import assess_risk
from app.services.weather_service import WeatherService
from app.models.weather import WeatherSnapshot


class AnalysisService:
    def __init__(self, weather_service: WeatherService, ml_service: MLService) -> None:
        self.weather_service = weather_service
        self.ml_service = ml_service

    async def analyze(self, latitude: float, longitude: float, location_name: str | None) -> AnalysisResponse:
        weather = await self.weather_service.get_weather(latitude, longitude)
        return self.analyze_weather(weather, location_name)

    def analyze_weather(self, weather: WeatherSnapshot, location_name: str | None) -> AnalysisResponse:
        if weather.freshness.status != "fresh":
            raise RuntimeDataError("Weather data is stale; analysis is unavailable")
        try:
            prediction = self.ml_service.predict(weather)
        except FileNotFoundError as exc:
            raise MLUnavailableError(str(exc)) from exc
        except MLArtifactError as exc:
            raise MLUnavailableError(str(exc)) from exc
        except ValueError as exc:
            raise RuntimeDataError(str(exc)) from exc
        probabilities = [hour.precipitation_probability_percent for hour in weather.hourly_forecast]
        if not probabilities or any(value is None for value in probabilities):
            raise RuntimeDataError("Forecast precipitation probability is required for risk calculation")
        risk = assess_risk(prediction.probability, weather.rainfall.forecast_next_24h_mm, max(float(value) for value in probabilities), weather.rainfall.recent_24h_mm)
        # The agent layer adds its evidence-constrained explanation.
        return AnalysisResponse(location_name=location_name, weather=weather, ml_prediction=prediction, risk=risk, status=weather.freshness.status)

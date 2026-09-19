from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:5173"
    weather_provider: str = "open_meteo"
    weather_http_timeout_seconds: float = 10.0
    weather_max_staleness_minutes: int = 90
    weather_cache_ttl_seconds: int = 300
    weather_max_retries: int = 2
    model_artifact_path: str = "models/weather_risk_model.joblib"
    nominatim_reverse_url: str = "https://nominatim.openstreetmap.org/reverse"
    nominatim_user_agent: str = "WeatherRiskAI/0.1 (student decision-support project)"
    llm_provider: str = ""
    llm_api_key: str = ""
    llm_model: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

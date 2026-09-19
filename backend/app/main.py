from contextlib import asynccontextmanager
from uuid import uuid4
import logging
from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes.weather import router as weather_router
from app.api.routes.analysis import router as analysis_router
from app.config import get_settings
from app.core.cache import TTLCache
from app.core.exceptions import InputValidationError, MLUnavailableError, ProviderError, RuntimeDataError
from app.ml.inference import MLService
from app.models.errors import ErrorDetail, ErrorResponse
from app.models.location import Location
from app.models.weather import WeatherSnapshot
from app.providers.open_meteo import OpenMeteoProvider
from app.services.location_service import LocationService
from app.services.weather_service import WeatherService
from app.services.analysis_service import AnalysisService
from app.agent.graph import WeatherRiskAgent
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def resolve_model_artifact_path(configured_path: str) -> Path:
    path = Path(configured_path)
    return path if path.is_absolute() else PROJECT_ROOT / path


def error_response(status_code: int, code: str, message: str, retryable: bool, request_id: str | None = None) -> JSONResponse:
    payload = ErrorResponse(error=ErrorDetail(code=code, message=message, request_id=request_id or str(uuid4()), retryable=retryable))
    return JSONResponse(status_code=status_code, content=payload.model_dump())


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    provider = OpenMeteoProvider(settings)
    app.state.location_service = LocationService(provider, TTLCache[list[Location]](settings.weather_cache_ttl_seconds), TTLCache(settings.weather_cache_ttl_seconds))
    app.state.weather_service = WeatherService(provider, TTLCache[WeatherSnapshot](settings.weather_cache_ttl_seconds))
    app.state.analysis_service = AnalysisService(app.state.weather_service, MLService(resolve_model_artifact_path(settings.model_artifact_path)))
    app.state.weather_risk_agent = WeatherRiskAgent(app.state.analysis_service)
    yield


app = FastAPI(title="WeatherRisk AI", version="0.1.0", lifespan=lifespan)
settings = get_settings()
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["Content-Type", "X-Request-ID"])
app.include_router(weather_router)
app.include_router(analysis_router)


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok", "version": app.version}


@app.exception_handler(ProviderError)
async def provider_error_handler(request: Request, exc: ProviderError) -> JSONResponse:
    return error_response(503 if exc.retryable else 502, "WEATHER_PROVIDER_ERROR", str(exc), exc.retryable, getattr(request.state, "request_id", None))


@app.exception_handler(MLUnavailableError)
async def ml_unavailable_handler(request: Request, exc: MLUnavailableError) -> JSONResponse:
    return error_response(503, "ML_MODEL_UNAVAILABLE", str(exc), False, getattr(request.state, "request_id", None))


@app.exception_handler(RuntimeDataError)
async def runtime_data_handler(request: Request, exc: RuntimeDataError) -> JSONResponse:
    return error_response(422, "ANALYSIS_INPUT_UNAVAILABLE", str(exc), False, getattr(request.state, "request_id", None))


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return error_response(422, "VALIDATION_ERROR", "Request parameters are invalid.", False, getattr(request.state, "request_id", None))


@app.exception_handler(InputValidationError)
async def input_validation_handler(request: Request, exc: InputValidationError) -> JSONResponse:
    return error_response(422, "VALIDATION_ERROR", str(exc), False, getattr(request.state, "request_id", None))


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request.state.request_id = request.headers.get("X-Request-ID", str(uuid4()))
    started = perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logging.getLogger("weatherrisk.request").exception("request_id=%s method=%s path=%s unhandled_error", request.state.request_id, request.method, request.url.path)
        response = error_response(500, "INTERNAL_ERROR", "An unexpected server error occurred.", False, request.state.request_id)
    logging.getLogger("weatherrisk.request").info("request_id=%s method=%s path=%s status=%s duration_ms=%.1f", request.state.request_id, request.method, request.url.path, response.status_code, (perf_counter() - started) * 1000)
    response.headers["X-Request-ID"] = request.state.request_id
    return response

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from app.models.location import Location, ReverseLocation
from app.models.weather import WeatherSnapshot
from app.services.location_service import LocationService
from app.services.weather_service import WeatherService
from app.core.exceptions import InputValidationError

router = APIRouter(tags=["weather"])


def location_service(request: Request) -> LocationService:
    return request.app.state.location_service


def weather_service(request: Request) -> WeatherService:
    return request.app.state.weather_service


@router.get("/locations", response_model=list[Location])
async def locations(query: Annotated[str, Query(min_length=1, max_length=100)], service: Annotated[LocationService, Depends(location_service)]) -> list[Location]:
    normalized_query = query.strip()
    if not normalized_query:
        raise InputValidationError("Location query must contain non-whitespace characters.")
    return await service.search(normalized_query)


@router.get("/locations/reverse", response_model=ReverseLocation)
async def reverse_location(latitude: Annotated[float, Query(ge=-90, le=90)], longitude: Annotated[float, Query(ge=-180, le=180)], service: Annotated[LocationService, Depends(location_service)]) -> ReverseLocation:
    return await service.reverse(latitude, longitude)


@router.get("/weather", response_model=WeatherSnapshot)
async def weather(latitude: Annotated[float, Query(ge=-90, le=90)], longitude: Annotated[float, Query(ge=-180, le=180)], service: Annotated[WeatherService, Depends(weather_service)]) -> WeatherSnapshot:
    return await service.get_weather(latitude, longitude)

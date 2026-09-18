from datetime import date
from typing import Protocol

from app.models.location import Location
from app.models.weather import WeatherSnapshot


class WeatherProvider(Protocol):
    async def search_locations(self, query: str) -> list[Location]: ...

    async def get_weather_snapshot(self, latitude: float, longitude: float) -> WeatherSnapshot: ...

    async def get_historical_hourly(self, latitude: float, longitude: float, start_date: date, end_date: date) -> dict: ...

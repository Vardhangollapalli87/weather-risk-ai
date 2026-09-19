import asyncio
from datetime import date, datetime, timedelta, timezone
from typing import Any

import httpx

from app.config import Settings
from app.core.exceptions import ProviderError, ProviderMalformedResponse
from app.core.freshness import assess_freshness
from app.models.location import Location, ReverseLocation
from app.models.weather import CurrentConditions, HourlyWeather, ProviderMetadata, RainfallSummary, WeatherSnapshot


class OpenMeteoProvider:
    geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
    forecast_url = "https://api.open-meteo.com/v1/forecast"
    archive_url = "https://archive-api.open-meteo.com/v1/archive"
    reverse_geocoding_url = "https://nominatim.openstreetmap.org/reverse"
    hourly_fields = ["temperature_2m", "relative_humidity_2m", "pressure_msl", "wind_speed_10m", "cloud_cover", "precipitation", "precipitation_probability", "weather_code"]

    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        self.settings = settings
        self._client = client

    async def _request(self, url: str, params: dict[str, Any], headers: dict[str, str] | None = None) -> dict[str, Any]:
        owns_client = self._client is None
        client = self._client or httpx.AsyncClient(timeout=self.settings.weather_http_timeout_seconds)
        try:
            for attempt in range(self.settings.weather_max_retries + 1):
                try:
                    response = await client.get(url, params=params, headers=headers)
                    if response.status_code >= 500:
                        raise ProviderError("Weather provider is temporarily unavailable")
                    response.raise_for_status()
                    payload = response.json()
                    if not isinstance(payload, dict):
                        raise ProviderMalformedResponse("Weather provider returned an invalid response", retryable=False)
                    return payload
                except (httpx.TimeoutException, httpx.NetworkError, ProviderError) as exc:
                    if attempt == self.settings.weather_max_retries:
                        if isinstance(exc, ProviderError):
                            raise exc
                        raise ProviderError("Weather provider request timed out") from exc
                    await asyncio.sleep(0.1 * (attempt + 1))
                except (httpx.HTTPStatusError, ValueError) as exc:
                    raise ProviderError("Weather provider request failed", retryable=False) from exc
        finally:
            if owns_client:
                await client.aclose()
        raise AssertionError("unreachable")

    async def search_locations(self, query: str) -> list[Location]:
        payload = await self._request(self.geocoding_url, {"name": query, "count": 10, "language": "en", "format": "json"})
        results = payload.get("results", [])
        if not isinstance(results, list):
            raise ProviderMalformedResponse("Weather provider returned malformed location results", retryable=False)
        try:
            return [Location(id=item.get("id"), name=item["name"], country=item.get("country"), admin1=item.get("admin1"), latitude=item["latitude"], longitude=item["longitude"], timezone=item.get("timezone")) for item in results]
        except (KeyError, TypeError, ValueError) as exc:
            raise ProviderMalformedResponse("Weather provider returned malformed location data", retryable=False) from exc

    async def reverse_geocode(self, latitude: float, longitude: float) -> ReverseLocation:
        payload = await self._request(
            self.reverse_geocoding_url,
            {"lat": latitude, "lon": longitude, "format": "jsonv2", "zoom": 10, "addressdetails": 1},
            {"User-Agent": "WeatherRiskAI/0.1 (student decision-support project)"},
        )
        try:
            address = payload["address"]
            if not isinstance(address, dict):
                raise TypeError("address is not an object")
            city = self._first_string(address, "city", "town", "village", "municipality", "county")
            name = self._first_string(address, "suburb", "neighbourhood", "city_district")
            state = self._first_string(address, "state", "state_district")
            country = self._first_string(address, "country")
            parts = [part for part in (name, city, state, country) if part]
            if not parts:
                raise ValueError("no locality fields")
            return ReverseLocation(name=name, city=city, state=state, country=country, display_name=", ".join(dict.fromkeys(parts)))
        except (KeyError, TypeError, ValueError) as exc:
            raise ProviderMalformedResponse("Reverse geocoding returned no usable locality data", retryable=False) from exc

    @staticmethod
    def _first_string(data: dict[str, Any], *keys: str) -> str | None:
        for key in keys:
            value = data.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return None

    async def get_weather_snapshot(self, latitude: float, longitude: float) -> WeatherSnapshot:
        # The provider's current timestamp may sit between hourly values; request
        # a small buffer so the normalized contract can always expose 24 future hours.
        payload = await self._request(self.forecast_url, {"latitude": latitude, "longitude": longitude, "timezone": "auto", "past_hours": 24, "forecast_hours": 30, "current": ",".join(field for field in self.hourly_fields if field != "precipitation_probability"), "hourly": ",".join(self.hourly_fields)})
        return self._parse_snapshot(payload, latitude, longitude)

    async def get_historical_hourly(self, latitude: float, longitude: float, start_date: date, end_date: date) -> dict:
        return await self._request(self.archive_url, {"latitude": latitude, "longitude": longitude, "start_date": start_date.isoformat(), "end_date": end_date.isoformat(), "timezone": "UTC", "hourly": ",".join(field for field in self.hourly_fields if field != "precipitation_probability")})

    def _parse_snapshot(self, payload: dict[str, Any], latitude: float, longitude: float) -> WeatherSnapshot:
        try:
            current = payload["current"]
            hourly = payload["hourly"]
            timezone_name = payload["timezone"]
            offset = int(payload.get("utc_offset_seconds", 0))
            times = hourly["time"]
            current_time = self._parse_time(current["time"], offset)
            items = [self._hourly_at(hourly, index, offset) for index in range(len(times))]
            current_index = min(range(len(items)), key=lambda index: abs((items[index].time - current_time).total_seconds()))
            recent = sum(item.precipitation_mm or 0 for item in items[max(0, current_index - 23):current_index + 1])
            recent_hourly = items[max(0, current_index - 23):current_index + 1]
            forecast = items[current_index + 1:current_index + 25]
            current_model = CurrentConditions(time=current_time, temperature_c=current.get("temperature_2m"), relative_humidity_percent=current.get("relative_humidity_2m"), pressure_msl_hpa=current.get("pressure_msl"), wind_speed_kmh=current.get("wind_speed_10m"), cloud_cover_percent=current.get("cloud_cover"), precipitation_mm=current.get("precipitation"), weather_code=current.get("weather_code"))
            reported_utc = current_time.astimezone(timezone.utc)
            return WeatherSnapshot(location=Location(name=f"{latitude:.4f}, {longitude:.4f}", latitude=latitude, longitude=longitude, timezone=timezone_name), timezone=timezone_name, current=current_model, recent_hourly=recent_hourly, hourly_forecast=forecast, rainfall=RainfallSummary(recent_24h_mm=round(recent, 2), forecast_next_24h_mm=round(sum(item.precipitation_mm or 0 for item in forecast), 2)), provider=ProviderMetadata(name="open-meteo", model=payload.get("model"), generation_time_ms=payload.get("generationtime_ms")), retrieved_at=datetime.now(timezone.utc), freshness=assess_freshness(reported_utc, self.settings.weather_max_staleness_minutes))
        except (KeyError, TypeError, ValueError, IndexError) as exc:
            raise ProviderMalformedResponse("Weather provider returned malformed weather data", retryable=False) from exc

    @staticmethod
    def _parse_time(value: str, offset_seconds: int) -> datetime:
        return datetime.fromisoformat(value).replace(tzinfo=timezone(timedelta(seconds=offset_seconds)))

    def _hourly_at(self, hourly: dict[str, Any], index: int, offset_seconds: int) -> HourlyWeather:
        def field(name: str) -> Any:
            values = hourly.get(name)
            return values[index] if isinstance(values, list) and len(values) > index else None
        return HourlyWeather(time=self._parse_time(field("time"), offset_seconds), temperature_c=field("temperature_2m"), relative_humidity_percent=field("relative_humidity_2m"), pressure_msl_hpa=field("pressure_msl"), wind_speed_kmh=field("wind_speed_10m"), cloud_cover_percent=field("cloud_cover"), precipitation_mm=field("precipitation"), precipitation_probability_percent=field("precipitation_probability"), weather_code=field("weather_code"))

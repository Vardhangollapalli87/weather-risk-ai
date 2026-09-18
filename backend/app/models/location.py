from pydantic import BaseModel, Field


class Location(BaseModel):
    id: int | None = None
    name: str
    country: str | None = None
    admin1: str | None = None
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    timezone: str | None = None

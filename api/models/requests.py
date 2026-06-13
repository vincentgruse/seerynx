from pydantic import BaseModel, field_validator, model_validator
from typing import Optional


class Sighting(BaseModel):
    common_name: str
    scientific_name: Optional[str] = None
    confidence: Optional[float] = None
    source: str
    photo_path: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None

    @field_validator("confidence")
    @classmethod
    def clamp_confidence(cls, v):
        if v is not None:
            return max(0.0, min(1.0, v))
        return v

    @field_validator("source")
    @classmethod
    def validate_source(cls, v):
        if v not in ("vision", "audio"):
            raise ValueError("source must be vision or audio")
        return v

    @field_validator("photo_path")
    @classmethod
    def validate_photo_path(cls, v):
        if v is not None:
            if ".." in v or v.startswith("/"):
                raise ValueError("Invalid photo path")
        return v


class DeleteSightingsRequest(BaseModel):
    ids: list[int]

    @field_validator("ids")
    @classmethod
    def validate_ids(cls, v):
        if not v:
            raise ValueError("ids must not be empty")
        return v


class DeleteSpeciesRequest(BaseModel):
    common_names: list[str]

    @field_validator("common_names")
    @classmethod
    def validate_common_names(cls, v):
        if not v:
            raise ValueError("common_names must not be empty")
        return v


class WeatherReading(BaseModel):
    temperature_c: float
    humidity: float

    @field_validator("temperature_c")
    @classmethod
    def validate_temp(cls, v):
        if not -50 <= v <= 60:
            raise ValueError("Temperature out of range")
        return v

    @field_validator("humidity")
    @classmethod
    def validate_humidity(cls, v):
        if not 0 <= v <= 100:
            raise ValueError("Humidity out of range")
        return v

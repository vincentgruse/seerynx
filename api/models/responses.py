from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SightingResponse(BaseModel):
    id: int
    timestamp: datetime
    common_name: str
    scientific_name: Optional[str]
    confidence: Optional[float]
    source: str
    photo_path: Optional[str]
    species_photo_path: Optional[str] = None
    lat: Optional[float]
    lon: Optional[float]


class SpeciesInfoResponse(BaseModel):
    common_name: str
    scientific_name: Optional[str]
    ebird_code: Optional[str]
    habitat: Optional[str]
    food: Optional[str]
    nesting: Optional[str]
    behavior: Optional[str]
    conservation: Optional[str]
    foods_list: Optional[str]
    feeder_types: Optional[str]
    notes: Optional[str]
    photo_path: Optional[str] = None
    category: Optional[str] = None


class WeatherResponse(BaseModel):
    id: int
    timestamp: datetime
    temperature_c: float
    humidity: float


class HeatmapEntry(BaseModel):
    hour: str
    audio_count: int
    vision_count: int


class StreakResponse(BaseModel):
    streak: int


class LifeListEntry(BaseModel):
    common_name: str
    scientific_name: Optional[str]
    first_seen: datetime
    species_photo_path: Optional[str] = None


class CalendarEntry(BaseModel):
    day: str
    count: int


class WeeklyEntry(BaseModel):
    week: str
    visits: int
    species_count: int


class AttractSuggestion(BaseModel):
    common_name: str
    food: Optional[str]
    feeder_types: Optional[str]


class HealthResponse(BaseModel):
    status: str
    last_sighting: Optional[str]
    uptime: str


class ModelStatus(BaseModel):
    birds_v1: bool
    efficientdet_lite0: bool


class HealthModelsResponse(BaseModel):
    status: str
    models: ModelStatus


class WeatherCorrelation(BaseModel):
    temperature_c: float
    humidity: float
    visit_count: int

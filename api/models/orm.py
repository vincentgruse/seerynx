from sqlalchemy import Integer, String, Float, DateTime, Text, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import Optional
from database import Base


class Sighting(Base):
    __tablename__ = "sightings"
    __table_args__ = (
        CheckConstraint("source IN ('vision', 'audio')", name="source_check"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    common_name: Mapped[str] = mapped_column(String(255), nullable=False)
    scientific_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(10), nullable=False)
    photo_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lon: Mapped[Optional[float]] = mapped_column(Float, nullable=True)


class SpeciesInfo(Base):
    __tablename__ = "species_info"

    common_name: Mapped[str] = mapped_column(String(255), primary_key=True)
    scientific_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ebird_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    habitat: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    food: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    nesting: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    behavior: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    conservation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    foods_list: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    feeder_types: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    photo_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)


class Weather(Base):
    __tablename__ = "weather"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    temperature_c: Mapped[float] = mapped_column(Float, nullable=False)
    humidity: Mapped[float] = mapped_column(Float, nullable=False)

"""Public dataclasses returned by the AirKorea client."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

RawRecord = Mapping[str, Any]


@dataclass(frozen=True)
class AirQualityMeasurement:
    """Hourly air quality measurement for one monitoring station."""

    station_name: str
    data_time: datetime | None
    mang_name: str | None
    sido_name: str | None
    khai_value: int | None
    khai_grade: int | None
    khai_grade_label: str | None
    so2_value: float | None
    co_value: float | None
    o3_value: float | None
    no2_value: float | None
    pm10_value: float | None
    pm10_value_24h: float | None
    pm25_value: float | None
    pm25_value_24h: float | None
    so2_grade: int | None
    co_grade: int | None
    o3_grade: int | None
    no2_grade: int | None
    pm10_grade: int | None
    pm10_grade_1h: int | None
    pm25_grade: int | None
    pm25_grade_1h: int | None
    raw: RawRecord = field(repr=False)


@dataclass(frozen=True)
class Station:
    """Air quality monitoring station metadata."""

    station_name: str
    addr: str | None
    year: int | None
    mang_name: str | None
    item: str | None
    lat: float | None
    lon: float | None
    raw: RawRecord = field(repr=False)


@dataclass(frozen=True)
class NearbyStation:
    """Monitoring station near a TM coordinate."""

    station_name: str
    addr: str | None
    distance_km: float | None
    raw: RawRecord = field(repr=False)


@dataclass(frozen=True)
class TmCoordinate:
    """AirKorea TM reference coordinate for an 읍면동 name."""

    sido_name: str | None
    sgg_name: str | None
    umd_name: str | None
    tm_x: float | None
    tm_y: float | None
    raw: RawRecord = field(repr=False)


@dataclass(frozen=True)
class ForecastNotice:
    """Fine-dust or ozone forecast notice."""

    data_time: str | None
    inform_code: str | None
    inform_data: date | None
    overall: str | None
    cause: str | None
    grade: str | None
    action: str | None
    image_urls: tuple[str, ...]
    raw: RawRecord = field(repr=False)


@dataclass(frozen=True)
class WeeklyForecastNotice:
    """Weekly PM2.5 forecast notice."""

    presented_at: str | None
    first_date: str | None
    first_content: str | None
    second_date: str | None
    second_content: str | None
    third_date: str | None
    third_content: str | None
    fourth_date: str | None
    fourth_content: str | None
    raw: RawRecord = field(repr=False)

"""Public dataclasses returned by the AirKorea client."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

from pyairkorea.codes import AirQualityGrade, InformCode, Pollutant
from pyairkorea.coords import LatLon

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

    @property
    def khai_grade_enum(self) -> AirQualityGrade | None:
        return AirQualityGrade.from_code(self.khai_grade)


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

    @property
    def coordinates(self) -> LatLon | None:
        if self.lat is None or self.lon is None:
            return None
        return LatLon(self.lat, self.lon)


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

    @property
    def inform_code_enum(self) -> InformCode | None:
        try:
            return InformCode(self.inform_code)
        except ValueError:
            return None


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


@dataclass(frozen=True)
class AirQualityStat:
    """Average/statistical air-quality row from AirKorea statistics APIs."""

    data_time: datetime | None
    measurement_date: date | None
    station_name: str | None
    sido_name: str | None
    city_name: str | None
    item_code: str | None
    data_gubun: str | None
    so2_value: float | None
    co_value: float | None
    o3_value: float | None
    no2_value: float | None
    pm10_value: float | None
    pm25_value: float | None
    region_values: Mapping[str, float | None] = field(default_factory=dict, repr=False)
    raw: RawRecord = field(repr=False, default_factory=dict)

    @property
    def item_code_enum(self) -> Pollutant | None:
        try:
            return Pollutant(self.item_code)
        except ValueError:
            return None


@dataclass(frozen=True)
class AdvisoryOccurrence:
    """Ozone or yellow-dust advisory occurrence row."""

    kind: str
    serial_number: int | None
    data_date: date | None
    district_name: str | None
    move_name: str | None
    issue_time: str | None
    issue_value: float | None
    clear_time: str | None
    clear_value: float | None
    max_value: float | None
    issue_level: int | None
    raw: RawRecord = field(repr=False)


@dataclass(frozen=True)
class DustAlarm:
    """PM10/PM2.5 advisory or warning row."""

    serial_number: int | None
    data_date: date | None
    district_name: str | None
    move_name: str | None
    item_code: str | None
    issue_gbn: str | None
    issue_date: date | None
    issue_time: str | None
    issue_value: float | None
    clear_date: date | None
    clear_time: str | None
    clear_value: float | None
    raw: RawRecord = field(repr=False)

    @property
    def item_code_enum(self) -> Pollutant | None:
        try:
            return Pollutant(self.item_code)
        except ValueError:
            return None


@dataclass(frozen=True)
class TrafficStat:
    """Daily API traffic count for an AirKorea service key."""

    connection_date: date | None
    service_name: str | None
    count: int | None
    raw: RawRecord = field(repr=False)


@dataclass(frozen=True)
class HighPm25Forecast:
    """High-concentration PM2.5 forecast row."""

    data_time: str | None
    inform_data: date | None
    overall: str | None
    cause: str | None
    grade: str | None
    raw: RawRecord = field(repr=False)


@dataclass(frozen=True)
class CaiMeasurement:
    """Real-time comprehensive air quality index (CAI) row."""

    station_name: str | None
    station_code: str | None
    data_time: datetime | None
    mang_name: str | None
    khai_value: int | None
    khai_grade: int | None
    khai_grade_label: str | None
    main_pollutant: str | None
    raw: RawRecord = field(repr=False)

    @property
    def khai_grade_enum(self) -> AirQualityGrade | None:
        return AirQualityGrade.from_code(self.khai_grade)


@dataclass(frozen=True)
class BackgroundConcentration:
    """Synthetic national-background concentration row for AI test data."""

    measurement_date: date | None
    measurement_time: str | None
    station_name: str | None
    so2_value: float | None
    co_value: float | None
    o3_value: float | None
    no2_value: float | None
    pm10_value: float | None
    pm25_value: float | None
    raw: RawRecord = field(repr=False)


@dataclass(frozen=True)
class EnglishAirQualityMeasurement:
    """English real-time measurement row."""

    station_name: str | None
    station_name_english: str | None
    data_time: datetime | None
    mang_name: str | None
    station_code: str | None
    khai_value: int | None
    khai_grade: int | None
    khai_grade_label: str | None
    so2_value: float | None
    co_value: float | None
    o3_value: float | None
    no2_value: float | None
    pm10_value: float | None
    pm25_value: float | None
    raw: RawRecord = field(repr=False)

    @property
    def khai_grade_enum(self) -> AirQualityGrade | None:
        return AirQualityGrade.from_code(self.khai_grade)


@dataclass(frozen=True)
class EnglishStation:
    """English monitoring-station metadata row."""

    station_name: str | None
    station_name_english: str | None
    road_address: str | None
    road_address_english: str | None
    lat: float | None
    lon: float | None
    raw: RawRecord = field(repr=False)

    @property
    def coordinates(self) -> LatLon | None:
        if self.lat is None or self.lon is None:
            return None
        return LatLon(self.lat, self.lon)

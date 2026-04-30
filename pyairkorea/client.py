"""Public AirKorea API client."""

from __future__ import annotations

import os
from collections.abc import Mapping
from datetime import date
from typing import Any

from pyairkorea._convert import (
    parse_data_time,
    strip_or_none,
    to_date_or_none,
    to_float_or_none,
    to_int_or_none,
)
from pyairkorea._http import HttpClient, SessionLike
from pyairkorea.codes import (
    grade_label,
    normalize_data_term,
    normalize_inform_code,
    validate_sido_name,
)
from pyairkorea.coords import wgs84_to_tm
from pyairkorea.exceptions import AirKoreaParseError
from pyairkorea.models import (
    AirQualityMeasurement,
    ForecastNotice,
    NearbyStation,
    Station,
    TmCoordinate,
    WeeklyForecastNotice,
)

DEFAULT_POLLUTION_BASE_URL = "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc"
DEFAULT_STATION_BASE_URL = "http://apis.data.go.kr/B552584/MsrstnInfoInqireSvc"


class AirKoreaClient:
    """Client for Korea Environment Corporation AirKorea public APIs."""

    def __init__(
        self,
        service_key: str,
        *,
        timeout: float = 10.0,
        retries: int = 3,
        retry_backoff: float = 0.3,
        session: SessionLike | None = None,
        pollution_base_url: str = DEFAULT_POLLUTION_BASE_URL,
        station_base_url: str = DEFAULT_STATION_BASE_URL,
    ) -> None:
        self._http = HttpClient(
            service_key,
            timeout=timeout,
            retries=retries,
            retry_backoff=retry_backoff,
            session=session,
        )
        self.pollution_base_url = pollution_base_url
        self.station_base_url = station_base_url

    @classmethod
    def from_env(cls, name: str = "AIRKOREA_SERVICE_KEY", **kwargs: Any) -> AirKoreaClient:
        try:
            service_key = os.environ[name]
        except KeyError as exc:
            raise ValueError(f"{name} is not set") from exc
        return cls(service_key=service_key, **kwargs)

    def station_measurements(
        self,
        station_name: str,
        *,
        data_term: str = "DAILY",
        page_no: int = 1,
        num_of_rows: int = 100,
        ver: str = "1.3",
    ) -> list[AirQualityMeasurement]:
        """Fetch real-time measurements for one monitoring station."""

        body = self._pollution(
            "getMsrstnAcctoRltmMesureDnsty",
            {
                "stationName": _required_text(station_name, "station_name"),
                "dataTerm": normalize_data_term(data_term),
                "pageNo": page_no,
                "numOfRows": num_of_rows,
                "ver": ver,
            },
        )
        return [_measurement(row) for row in _items(body)]

    def latest_station_measurement(
        self,
        station_name: str,
        *,
        data_term: str = "DAILY",
        ver: str = "1.3",
    ) -> AirQualityMeasurement | None:
        """Return the first measurement row for a station, or ``None`` when empty."""

        rows = self.station_measurements(
            station_name,
            data_term=data_term,
            num_of_rows=1,
            ver=ver,
        )
        return rows[0] if rows else None

    def sido_measurements(
        self,
        sido_name: str,
        *,
        page_no: int = 1,
        num_of_rows: int = 100,
        ver: str = "1.3",
    ) -> list[AirQualityMeasurement]:
        """Fetch real-time measurements for all stations in one 시도."""

        body = self._pollution(
            "getCtprvnRltmMesureDnsty",
            {
                "sidoName": validate_sido_name(sido_name),
                "pageNo": page_no,
                "numOfRows": num_of_rows,
                "ver": ver,
            },
        )
        return [_measurement(row) for row in _items(body)]

    def unhealthy_stations(
        self,
        *,
        page_no: int = 1,
        num_of_rows: int = 100,
    ) -> list[AirQualityMeasurement]:
        """Fetch stations where the comprehensive air-quality index is unhealthy or worse."""

        body = self._pollution(
            "getUnityAirEnvrnIdexSnstiveAboveMsrstnList",
            {
                "pageNo": page_no,
                "numOfRows": num_of_rows,
            },
        )
        return [_measurement(row) for row in _items(body)]

    def forecast_notices(
        self,
        *,
        search_date: str | date | None = None,
        inform_code: str | None = None,
        page_no: int = 1,
        num_of_rows: int = 100,
    ) -> list[ForecastNotice]:
        """Fetch fine-dust or ozone forecast notices."""

        body = self._pollution(
            "getMinuDustFrcstDspth",
            {
                "searchDate": _date_param(search_date),
                "InformCode": normalize_inform_code(inform_code),
                "pageNo": page_no,
                "numOfRows": num_of_rows,
            },
        )
        return [_forecast_notice(row) for row in _items(body)]

    def weekly_forecasts(
        self,
        *,
        search_date: str | date | None = None,
        page_no: int = 1,
        num_of_rows: int = 100,
    ) -> list[WeeklyForecastNotice]:
        """Fetch weekly PM2.5 forecast notices."""

        body = self._pollution(
            "getMinuDustWeekFrcstDspth",
            {
                "searchDate": _date_param(search_date),
                "pageNo": page_no,
                "numOfRows": num_of_rows,
            },
        )
        return [_weekly_forecast(row) for row in _items(body)]

    def stations(
        self,
        *,
        addr: str | None = None,
        station_name: str | None = None,
        page_no: int = 1,
        num_of_rows: int = 100,
    ) -> list[Station]:
        """Fetch monitoring-station metadata."""

        body = self._station(
            "getMsrstnList",
            {
                "addr": addr,
                "stationName": station_name,
                "pageNo": page_no,
                "numOfRows": num_of_rows,
            },
        )
        return [_station_metadata(row) for row in _items(body)]

    def nearby_stations(
        self,
        *,
        tm_x: float | None = None,
        tm_y: float | None = None,
        lat: float | None = None,
        lon: float | None = None,
        ver: str | None = None,
    ) -> list[NearbyStation]:
        """Fetch monitoring stations near a TM coordinate or WGS84 latitude/longitude."""

        query_x, query_y = _coordinates(tm_x=tm_x, tm_y=tm_y, lat=lat, lon=lon)
        body = self._station(
            "getNearbyMsrstnList",
            {
                "tmX": query_x,
                "tmY": query_y,
                "ver": ver,
            },
        )
        return [_nearby_station(row) for row in _items(body)]

    def tm_coordinates(
        self,
        umd_name: str,
        *,
        page_no: int = 1,
        num_of_rows: int = 100,
    ) -> list[TmCoordinate]:
        """Fetch AirKorea TM reference coordinates by 읍면동 name."""

        body = self._station(
            "getTMStdrCrdnt",
            {
                "umdName": _required_text(umd_name, "umd_name"),
                "pageNo": page_no,
                "numOfRows": num_of_rows,
            },
        )
        return [_tm_coordinate(row) for row in _items(body)]

    def measurement_near(
        self,
        *,
        lat: float,
        lon: float,
        data_term: str = "DAILY",
        ver: str = "1.3",
    ) -> AirQualityMeasurement | None:
        """Find the nearest station to WGS84 coordinates and return its latest measurement."""

        stations = self.nearby_stations(lat=lat, lon=lon)
        if not stations:
            return None
        return self.latest_station_measurement(
            stations[0].station_name,
            data_term=data_term,
            ver=ver,
        )

    def _pollution(self, endpoint: str, params: Mapping[str, Any]) -> Mapping[str, Any]:
        return self._http.get_body(self.pollution_base_url, endpoint, params)

    def _station(self, endpoint: str, params: Mapping[str, Any]) -> Mapping[str, Any]:
        return self._http.get_body(self.station_base_url, endpoint, params)


def _items(body: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    raw_items = body.get("items")
    if raw_items is None or raw_items == "":
        return []
    if isinstance(raw_items, Mapping) and "item" in raw_items:
        raw_items = raw_items["item"]
    if raw_items is None or raw_items == "":
        return []
    if isinstance(raw_items, Mapping):
        return [raw_items]
    if isinstance(raw_items, list) and all(isinstance(item, Mapping) for item in raw_items):
        return raw_items
    raise AirKoreaParseError("response.body.items must be an object or list")


def _measurement(row: Mapping[str, Any]) -> AirQualityMeasurement:
    try:
        khai_grade = to_int_or_none(row.get("khaiGrade"))
        return AirQualityMeasurement(
            station_name=_required_text(row.get("stationName"), "stationName"),
            data_time=parse_data_time(row.get("dataTime")),
            mang_name=strip_or_none(row.get("mangName")),
            sido_name=strip_or_none(row.get("sidoName")),
            khai_value=to_int_or_none(row.get("khaiValue")),
            khai_grade=khai_grade,
            khai_grade_label=grade_label(khai_grade),
            so2_value=to_float_or_none(row.get("so2Value")),
            co_value=to_float_or_none(row.get("coValue")),
            o3_value=to_float_or_none(row.get("o3Value")),
            no2_value=to_float_or_none(row.get("no2Value")),
            pm10_value=to_float_or_none(row.get("pm10Value")),
            pm10_value_24h=to_float_or_none(row.get("pm10Value24")),
            pm25_value=to_float_or_none(row.get("pm25Value")),
            pm25_value_24h=to_float_or_none(row.get("pm25Value24")),
            so2_grade=to_int_or_none(row.get("so2Grade")),
            co_grade=to_int_or_none(row.get("coGrade")),
            o3_grade=to_int_or_none(row.get("o3Grade")),
            no2_grade=to_int_or_none(row.get("no2Grade")),
            pm10_grade=to_int_or_none(row.get("pm10Grade")),
            pm10_grade_1h=to_int_or_none(row.get("pm10Grade1h")),
            pm25_grade=to_int_or_none(row.get("pm25Grade")),
            pm25_grade_1h=to_int_or_none(row.get("pm25Grade1h")),
            raw=row,
        )
    except (TypeError, ValueError) as exc:
        raise AirKoreaParseError(f"malformed measurement item: {row!r}") from exc


def _station_metadata(row: Mapping[str, Any]) -> Station:
    try:
        return Station(
            station_name=_required_text(row.get("stationName"), "stationName"),
            addr=strip_or_none(row.get("addr")),
            year=to_int_or_none(row.get("year")),
            mang_name=strip_or_none(row.get("mangName")),
            item=strip_or_none(row.get("item")),
            lat=to_float_or_none(row.get("dmX")),
            lon=to_float_or_none(row.get("dmY")),
            raw=row,
        )
    except (TypeError, ValueError) as exc:
        raise AirKoreaParseError(f"malformed station item: {row!r}") from exc


def _nearby_station(row: Mapping[str, Any]) -> NearbyStation:
    try:
        return NearbyStation(
            station_name=_required_text(row.get("stationName"), "stationName"),
            addr=strip_or_none(row.get("addr")),
            distance_km=to_float_or_none(row.get("tm")),
            raw=row,
        )
    except (TypeError, ValueError) as exc:
        raise AirKoreaParseError(f"malformed nearby station item: {row!r}") from exc


def _tm_coordinate(row: Mapping[str, Any]) -> TmCoordinate:
    try:
        return TmCoordinate(
            sido_name=strip_or_none(row.get("sidoName")),
            sgg_name=strip_or_none(row.get("sggName")),
            umd_name=strip_or_none(row.get("umdName")),
            tm_x=to_float_or_none(row.get("tmX")),
            tm_y=to_float_or_none(row.get("tmY")),
            raw=row,
        )
    except (TypeError, ValueError) as exc:
        raise AirKoreaParseError(f"malformed TM coordinate item: {row!r}") from exc


def _forecast_notice(row: Mapping[str, Any]) -> ForecastNotice:
    try:
        image_urls = tuple(
            url
            for url in (strip_or_none(row.get(f"imageUrl{index}")) for index in range(1, 10))
            if url is not None
        )
        return ForecastNotice(
            data_time=strip_or_none(row.get("dataTime")),
            inform_code=strip_or_none(row.get("informCode")),
            inform_data=to_date_or_none(row.get("informData")),
            overall=strip_or_none(row.get("informOverall") or row.get("infornOverall")),
            cause=strip_or_none(row.get("informCause")),
            grade=strip_or_none(row.get("informGrade")),
            action=strip_or_none(row.get("actionKnack")),
            image_urls=image_urls,
            raw=row,
        )
    except (TypeError, ValueError) as exc:
        raise AirKoreaParseError(f"malformed forecast notice item: {row!r}") from exc


def _weekly_forecast(row: Mapping[str, Any]) -> WeeklyForecastNotice:
    return WeeklyForecastNotice(
        presented_at=strip_or_none(row.get("presnatnDt") or row.get("presentnDt")),
        first_date=strip_or_none(row.get("frcstOneDt")),
        first_content=strip_or_none(row.get("frcstOneCn")),
        second_date=strip_or_none(row.get("frcstTwoDt")),
        second_content=strip_or_none(row.get("frcstTwoCn")),
        third_date=strip_or_none(row.get("frcstThreeDt")),
        third_content=strip_or_none(row.get("frcstThreeCn")),
        fourth_date=strip_or_none(row.get("frcstFourDt")),
        fourth_content=strip_or_none(row.get("frcstFourCn")),
        raw=row,
    )


def _coordinates(
    *,
    tm_x: float | None,
    tm_y: float | None,
    lat: float | None,
    lon: float | None,
) -> tuple[float, float]:
    has_tm = tm_x is not None or tm_y is not None
    has_latlon = lat is not None or lon is not None
    if has_tm and has_latlon:
        raise ValueError("Provide either tm_x/tm_y or lat/lon, not both")
    if has_tm:
        if tm_x is None or tm_y is None:
            raise ValueError("Both tm_x and tm_y are required")
        return tm_x, tm_y
    if lat is None or lon is None:
        raise ValueError("Either tm_x/tm_y or lat/lon is required")
    return wgs84_to_tm(lat, lon)


def _required_text(value: Any, field: str) -> str:
    text = strip_or_none(value)
    if text is None:
        raise ValueError(f"{field} is required")
    return text


def _date_param(value: str | date | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value.isoformat()
    return _required_text(value, "search_date")

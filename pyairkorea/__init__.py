"""Python client for Korea Environment Corporation AirKorea APIs."""

from pyairkorea.client import SUPPORTED_ENDPOINTS, AirKoreaClient
from pyairkorea.coords import tm_to_wgs84, wgs84_to_tm
from pyairkorea.exceptions import (
    AirKoreaAuthError,
    AirKoreaError,
    AirKoreaNetworkError,
    AirKoreaNoDataError,
    AirKoreaParseError,
    AirKoreaRateLimitError,
    AirKoreaRequestError,
    AirKoreaServerError,
)
from pyairkorea.models import (
    AdvisoryOccurrence,
    AirQualityMeasurement,
    AirQualityStat,
    BackgroundConcentration,
    CaiMeasurement,
    DustAlarm,
    EnglishAirQualityMeasurement,
    EnglishStation,
    ForecastNotice,
    HighPm25Forecast,
    NearbyStation,
    Station,
    TmCoordinate,
    TrafficStat,
    WeeklyForecastNotice,
)

__version__ = "0.2.0"

__all__ = [
    "AirKoreaAuthError",
    "AirKoreaClient",
    "AirKoreaError",
    "AirKoreaNetworkError",
    "AirKoreaNoDataError",
    "AirKoreaParseError",
    "AirKoreaRateLimitError",
    "AirKoreaRequestError",
    "AirKoreaServerError",
    "AirQualityMeasurement",
    "AirQualityStat",
    "AdvisoryOccurrence",
    "BackgroundConcentration",
    "CaiMeasurement",
    "DustAlarm",
    "EnglishAirQualityMeasurement",
    "EnglishStation",
    "ForecastNotice",
    "HighPm25Forecast",
    "NearbyStation",
    "Station",
    "SUPPORTED_ENDPOINTS",
    "TmCoordinate",
    "TrafficStat",
    "WeeklyForecastNotice",
    "__version__",
    "tm_to_wgs84",
    "wgs84_to_tm",
]

"""Python client for Korea Environment Corporation AirKorea APIs."""

from pyairkorea.client import AirKoreaClient
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
    AirQualityMeasurement,
    ForecastNotice,
    NearbyStation,
    Station,
    TmCoordinate,
    WeeklyForecastNotice,
)

__version__ = "0.1.0"

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
    "ForecastNotice",
    "NearbyStation",
    "Station",
    "TmCoordinate",
    "WeeklyForecastNotice",
    "__version__",
    "tm_to_wgs84",
    "wgs84_to_tm",
]

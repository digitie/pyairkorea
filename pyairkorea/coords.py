"""Coordinate conversion helpers for AirKorea TM requests."""

from __future__ import annotations

from functools import lru_cache

DEFAULT_AIRKOREA_TM_CRS = "EPSG:2097"
WGS84_CRS = "EPSG:4326"


def validate_latlon(lat: float, lon: float) -> None:
    if not -90.0 <= lat <= 90.0:
        raise ValueError("lat must be between -90 and 90")
    if not -180.0 <= lon <= 180.0:
        raise ValueError("lon must be between -180 and 180")


def wgs84_to_tm(
    lat: float,
    lon: float,
    *,
    target_crs: str = DEFAULT_AIRKOREA_TM_CRS,
) -> tuple[float, float]:
    """Convert WGS84 latitude/longitude to AirKorea legacy TM coordinates.

    AirKorea's nearby-station endpoint documents TM central-belt coordinates.
    Historical AirKorea examples align with EPSG:2097. If you already have
    road-address API coordinates, pass those directly to the client instead.
    """

    validate_latlon(lat, lon)
    transformer = _transformer(WGS84_CRS, target_crs)
    tm_x, tm_y = transformer.transform(lon, lat)
    return float(tm_x), float(tm_y)


def tm_to_wgs84(
    tm_x: float,
    tm_y: float,
    *,
    source_crs: str = DEFAULT_AIRKOREA_TM_CRS,
) -> tuple[float, float]:
    """Convert AirKorea legacy TM coordinates to WGS84 latitude/longitude."""

    transformer = _transformer(source_crs, WGS84_CRS)
    lon, lat = transformer.transform(tm_x, tm_y)
    return float(lat), float(lon)


@lru_cache(maxsize=16)
def _transformer(source_crs: str, target_crs: str):  # type: ignore[no-untyped-def]
    try:
        from pyproj import Transformer
    except ModuleNotFoundError as exc:  # pragma: no cover - dependency is required by package
        raise RuntimeError("pyproj is required for AirKorea coordinate conversion") from exc
    return Transformer.from_crs(source_crs, target_crs, always_xy=True)

from __future__ import annotations

import pytest

from pyairkorea.coords import tm_to_wgs84, validate_latlon, wgs84_to_tm


def test_wgs84_to_airkorea_tm_default_matches_legacy_examples() -> None:
    tm_x, tm_y = wgs84_to_tm(37.5665, 126.9780)

    assert tm_x == pytest.approx(198242, abs=2)
    assert tm_y == pytest.approx(451580, abs=2)


def test_tm_to_wgs84_roundtrip() -> None:
    lat, lon = 37.5665, 126.9780
    tm_x, tm_y = wgs84_to_tm(lat, lon)

    out_lat, out_lon = tm_to_wgs84(tm_x, tm_y)

    assert out_lat == pytest.approx(lat, abs=1e-6)
    assert out_lon == pytest.approx(lon, abs=1e-6)


@pytest.mark.parametrize(
    ("lat", "lon"),
    [
        (-91.0, 127.0),
        (91.0, 127.0),
        (37.0, -181.0),
        (37.0, 181.0),
    ],
)
def test_validate_latlon_rejects_out_of_range(lat: float, lon: float) -> None:
    with pytest.raises(ValueError):
        validate_latlon(lat, lon)

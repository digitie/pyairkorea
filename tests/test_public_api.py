from __future__ import annotations

import importlib.resources

import airkorea


def test_package_all_contains_recommended_public_api() -> None:
    recommended = {
        "AirKoreaClient",
        "AirKoreaCallContext",
        "AirKoreaPage",
        "RawRecord",
        "PlaceCoordinate",
        "LatLon",
        "TmPoint",
        "sanitize_request_params",
        "make_cache_key",
        "has_next_page",
        "next_page_no",
        "iter_paginated_pages",
    }

    assert recommended.issubset(set(airkorea.__all__))


def test_py_typed_marker_is_present_in_package() -> None:
    marker = importlib.resources.files("airkorea").joinpath("py.typed")

    assert marker.is_file()

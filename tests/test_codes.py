from __future__ import annotations

import pytest

from pyairkorea.codes import (
    grade_label,
    normalize_data_term,
    normalize_inform_code,
    validate_sido_name,
)


def test_grade_label() -> None:
    assert grade_label("1") == "좋음"
    assert grade_label(2) == "보통"
    assert grade_label("3") == "나쁨"
    assert grade_label("4") == "매우나쁨"
    assert grade_label("5") is None
    assert grade_label("-") is None


def test_normalize_data_term() -> None:
    assert normalize_data_term("daily") == "DAILY"
    assert normalize_data_term("MONTH") == "MONTH"
    assert normalize_data_term("3month") == "3MONTH"

    with pytest.raises(ValueError):
        normalize_data_term("YEAR")


def test_normalize_inform_code() -> None:
    assert normalize_inform_code(None) is None
    assert normalize_inform_code("pm10") == "PM10"
    assert normalize_inform_code("PM25") == "PM25"
    assert normalize_inform_code("o3") == "O3"

    with pytest.raises(ValueError):
        normalize_inform_code("NO2")


def test_validate_sido_name() -> None:
    assert validate_sido_name("서울") == "서울"
    assert validate_sido_name(" 경기 ") == "경기"

    with pytest.raises(ValueError):
        validate_sido_name("서울특별시")

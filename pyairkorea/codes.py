"""AirKorea code labels and parameter validators."""

from __future__ import annotations

from typing import Any

GRADE_LABELS = {
    1: "좋음",
    2: "보통",
    3: "나쁨",
    4: "매우나쁨",
}

INFORM_CODES = {"PM10", "PM25", "O3"}
DATA_TERMS = {"DAILY", "MONTH", "3MONTH"}
SIDO_NAMES = {
    "서울",
    "부산",
    "대구",
    "인천",
    "광주",
    "대전",
    "울산",
    "경기",
    "강원",
    "충북",
    "충남",
    "전북",
    "전남",
    "경북",
    "경남",
    "제주",
    "세종",
}

POLLUTANT_UNITS = {
    "so2": "ppm",
    "co": "ppm",
    "o3": "ppm",
    "no2": "ppm",
    "pm10": "㎍/㎥",
    "pm25": "㎍/㎥",
    "khai": "index",
}


def grade_label(value: Any) -> str | None:
    """Return the Korean grade label for AirKorea grade codes 1-4."""

    if value is None:
        return None
    try:
        code = int(str(value).strip())
    except ValueError:
        return None
    return GRADE_LABELS.get(code)


def normalize_data_term(value: str) -> str:
    term = value.strip().upper()
    if term not in DATA_TERMS:
        raise ValueError(f"data_term must be one of {sorted(DATA_TERMS)}")
    return term


def normalize_inform_code(value: str | None) -> str | None:
    if value is None:
        return None
    code = value.strip().upper()
    if code not in INFORM_CODES:
        raise ValueError(f"inform_code must be one of {sorted(INFORM_CODES)}")
    return code


def validate_sido_name(value: str) -> str:
    name = value.strip()
    if name not in SIDO_NAMES:
        raise ValueError(f"sido_name must be one of {sorted(SIDO_NAMES)}")
    return name

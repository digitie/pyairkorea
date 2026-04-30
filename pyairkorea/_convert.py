"""Type conversion helpers for raw AirKorea values."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from typing import Any

KST = timezone(timedelta(hours=9))

_EMPTY_TEXTS = {"", "-", "null", "none", "nan"}


def strip_or_none(value: Any) -> str | None:
    """Strip a raw API value and normalize blank placeholders to ``None``."""

    if value is None:
        return None
    text = str(value).strip()
    if text.lower() in _EMPTY_TEXTS:
        return None
    return text


def to_float_or_none(value: Any) -> float | None:
    text = strip_or_none(value)
    if text is None:
        return None
    return float(text.replace(",", ""))


def to_int_or_none(value: Any) -> int | None:
    text = strip_or_none(value)
    if text is None:
        return None
    try:
        return int(Decimal(text.replace(",", "")))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"invalid integer value: {value!r}") from exc


def to_date_or_none(value: Any) -> date | None:
    text = strip_or_none(value)
    if text is None:
        return None
    for fmt in ("%Y-%m-%d", "%Y%m%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"invalid date value: {value!r}")


def parse_data_time(value: Any) -> datetime | None:
    """Parse common AirKorea KST data-time strings into aware datetimes."""

    text = strip_or_none(value)
    if text is None:
        return None
    normalized = text.replace("시 발표", ":00").replace("시", ":00")
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H%M", "%Y%m%d%H%M"):
        try:
            return datetime.strptime(normalized, fmt).replace(tzinfo=KST)
        except ValueError:
            continue
    if len(normalized) == 10:
        try:
            return datetime.strptime(normalized, "%Y-%m-%d").replace(tzinfo=KST)
        except ValueError:
            pass
    raise ValueError(f"invalid AirKorea data time: {value!r}")

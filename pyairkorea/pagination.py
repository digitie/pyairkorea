"""Pagination helpers for data.go.kr-style AirKorea response bodies."""

from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping
from typing import Any, TypeVar

from pyairkorea.models import AirKoreaPage

T = TypeVar("T")


def has_next_page(body: Mapping[str, Any]) -> bool:
    """Return whether a data.go.kr response body has another page."""

    page_no = _int_from_body(body, "pageNo", default=1)
    num_of_rows = _int_from_body(body, "numOfRows", default=0)
    total_count = _int_from_body(body, "totalCount", default=0)
    if page_no < 1 or num_of_rows < 1 or total_count < 1:
        return False
    return page_no * num_of_rows < total_count


def next_page_no(body: Mapping[str, Any]) -> int | None:
    """Return the next page number, or ``None`` when the body is the last page."""

    if not has_next_page(body):
        return None
    return _int_from_body(body, "pageNo", default=1) + 1


def iter_paginated_pages(
    fetch_page: Callable[[int, int], AirKoreaPage[T]],
    *,
    page_no: int = 1,
    num_of_rows: int = 100,
    max_pages: int | None = None,
    max_items: int | None = None,
) -> Iterator[AirKoreaPage[T]]:
    """Iterate AirKorea pages until page metadata says there is no next page."""

    _validate_pagination_input(
        page_no=page_no,
        num_of_rows=num_of_rows,
        max_pages=max_pages,
        max_items=max_items,
    )
    current_page_no = page_no
    pages_seen = 0
    items_seen = 0

    while True:
        if max_pages is not None and pages_seen >= max_pages:
            return
        if max_items is not None and items_seen >= max_items:
            return

        page = fetch_page(current_page_no, num_of_rows)
        if page.is_empty:
            return

        yield page
        pages_seen += 1
        items_seen += len(page.items)

        if not page.has_next_page:
            return
        current_page_no = page.next_page_no or current_page_no + 1


def _validate_pagination_input(
    *,
    page_no: int,
    num_of_rows: int,
    max_pages: int | None,
    max_items: int | None,
) -> None:
    if page_no < 1:
        raise ValueError("page_no must be >= 1")
    if num_of_rows < 1:
        raise ValueError("num_of_rows must be >= 1")
    if max_pages is not None and max_pages < 0:
        raise ValueError("max_pages must be >= 0")
    if max_items is not None and max_items < 0:
        raise ValueError("max_items must be >= 0")


def _int_from_body(body: Mapping[str, Any], key: str, *, default: int) -> int:
    try:
        return int(str(body.get(key, default)).strip())
    except (TypeError, ValueError):
        return default

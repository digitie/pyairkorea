"""AirKorea/data.go.kr 오류 매핑을 포함한 HTTP 헬퍼."""

from __future__ import annotations

from collections.abc import Mapping
from time import sleep
from typing import Any, Protocol, cast

import requests

from pyairkorea.exceptions import (
    AirKoreaAuthError,
    AirKoreaNetworkError,
    AirKoreaNoDataError,
    AirKoreaParseError,
    AirKoreaRateLimitError,
    AirKoreaRequestError,
    AirKoreaServerError,
)


class ResponseLike(Protocol):
    status_code: int
    text: str

    def json(self) -> Any: ...


class SessionLike(Protocol):
    def get(self, url: str, *, params: Mapping[str, Any], timeout: float) -> ResponseLike: ...


TRANSIENT_STATUSES = {500, 502, 503, 504}


class HttpClient:
    """AirKorea 서비스군이 공유하는 작은 요청 래퍼."""

    def __init__(
        self,
        service_key: str,
        *,
        session: SessionLike | None = None,
        timeout: float = 10.0,
        retries: int = 3,
        retry_backoff: float = 0.3,
    ) -> None:
        if not service_key:
            raise AirKoreaAuthError("service_key is required")
        self._service_key = service_key
        self._session = cast(SessionLike, session or requests.Session())
        self._timeout = timeout
        self._retries = max(0, retries)
        self._retry_backoff = max(0.0, retry_backoff)

    def get_body(
        self,
        base_url: str,
        endpoint: str,
        params: Mapping[str, Any],
        *,
        service_key_param: str = "serviceKey",
        format_param: str = "returnType",
        format_value: str = "json",
    ) -> Mapping[str, Any]:
        response = self._request(
            f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}",
            self._params(
                params,
                service_key_param=service_key_param,
                format_param=format_param,
                format_value=format_value,
            ),
        )
        try:
            payload = response.json()
        except ValueError as exc:
            _raise_for_plain_text(response.text)
            raise AirKoreaParseError(f"failed to parse JSON response: {exc}") from exc

        if not isinstance(payload, Mapping):
            raise AirKoreaParseError("JSON response root is not an object")
        return _extract_body(payload)

    def _request(self, url: str, params: Mapping[str, Any]) -> ResponseLike:
        last_error: requests.RequestException | None = None
        for attempt in range(self._retries + 1):
            try:
                response = self._session.get(url, params=params, timeout=self._timeout)
            except (requests.ConnectionError, requests.Timeout) as exc:
                last_error = exc
                if attempt < self._retries:
                    self._sleep_before_retry(attempt)
                    continue
                raise AirKoreaNetworkError(str(exc)) from exc

            if response.status_code in TRANSIENT_STATUSES and attempt < self._retries:
                self._sleep_before_retry(attempt)
                continue
            _raise_for_status(response)
            return response

        raise AirKoreaNetworkError(str(last_error) if last_error else "request failed")

    def _params(
        self,
        params: Mapping[str, Any],
        *,
        service_key_param: str,
        format_param: str,
        format_value: str,
    ) -> dict[str, Any]:
        query: dict[str, Any] = {
            service_key_param: self._service_key,
            format_param: format_value,
        }
        for key, value in params.items():
            if value is not None:
                query[key] = value
        return query

    def _sleep_before_retry(self, attempt: int) -> None:
        if self._retry_backoff <= 0:
            return
        sleep(self._retry_backoff * (2**attempt))


def _raise_for_status(response: ResponseLike) -> None:
    status = response.status_code
    text = response.text[:300]
    if status in {401, 403}:
        raise AirKoreaAuthError(f"HTTP {status}: {text}")
    if status == 429:
        raise AirKoreaRateLimitError(f"HTTP {status}: {text}")
    if 400 <= status < 500:
        raise AirKoreaRequestError(f"HTTP {status}: {text}")
    if 500 <= status < 600:
        raise AirKoreaServerError(f"HTTP {status}: {text}")


def _raise_for_plain_text(text: str) -> None:
    upper = text.upper()
    preview = text[:300]
    if "SERVICE_KEY" in upper or "SERVICE KEY" in upper:
        raise AirKoreaAuthError(preview)
    if "LIMIT" in upper or "LIMITED" in upper or "초과" in text:
        raise AirKoreaRateLimitError(preview)


def _extract_body(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    response = payload.get("response")
    if not isinstance(response, Mapping):
        raise AirKoreaParseError("response object is missing")
    header = response.get("header")
    if not isinstance(header, Mapping):
        raise AirKoreaParseError("response.header object is missing")

    code = str(header.get("resultCode", "")).strip()
    message = str(header.get("resultMsg", "")).strip()
    if code != "00":
        _raise_for_result_code(code, message)

    body = response.get("body", {})
    if not isinstance(body, Mapping):
        raise AirKoreaParseError("response.body is not an object")
    return body


def _raise_for_result_code(code: str, message: str) -> None:
    text = f"AirKorea API returned {code}: {message}"
    upper = message.upper()
    if code in {"20", "30", "31"} or "SERVICE_KEY" in upper:
        raise AirKoreaAuthError(text)
    if code == "03":
        raise AirKoreaNoDataError(text)
    if code == "22" or "LIMIT" in upper:
        raise AirKoreaRateLimitError(text)
    if code in {"04", "99"}:
        raise AirKoreaServerError(text)
    raise AirKoreaRequestError(text)

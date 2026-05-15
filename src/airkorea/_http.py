"""AirKorea/data.go.kr 오류 매핑을 포함한 HTTP 헬퍼."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from time import sleep
from typing import Any, Protocol, cast

import requests

from airkorea.exceptions import (
    AirKoreaAuthError,
    AirKoreaNetworkError,
    AirKoreaNoDataError,
    AirKoreaParseError,
    AirKoreaRateLimitError,
    AirKoreaRequestError,
    AirKoreaServerError,
)
from airkorea.metadata import normalize_service_key, sanitize_request_params


class ResponseLike(Protocol):
    status_code: int
    text: str

    def json(self) -> Any: ...


class SessionLike(Protocol):
    def get(self, url: str, *, params: Mapping[str, Any], timeout: float) -> ResponseLike: ...


TRANSIENT_STATUSES = {500, 502, 503, 504}


@dataclass(frozen=True)
class HttpExchange:
    """디버그 fixture 저장을 위해 인증키를 제거해 보관한 HTTP 교환 기록."""

    method: str
    url: str
    request_params: Mapping[str, Any]
    status_code: int
    response_headers: Mapping[str, str]
    response_body: Mapping[str, Any] | None = None
    response_json: Mapping[str, Any] | None = None
    response_text: str = ""


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
        normalized_service_key = normalize_service_key(service_key)
        if not normalized_service_key:
            raise AirKoreaAuthError("service_key is required")
        self._service_key = normalized_service_key
        self._session = cast(SessionLike, session or requests.Session())
        self._timeout = timeout
        self._retries = max(0, retries)
        self._retry_backoff = max(0.0, retry_backoff)
        self._exchanges: list[HttpExchange] = []

    @property
    def exchanges(self) -> tuple[HttpExchange, ...]:
        """현재 클라이언트가 기록한 인증키 제거 HTTP 교환 목록입니다."""

        return tuple(self._exchanges)

    @property
    def last_exchange(self) -> HttpExchange | None:
        """마지막 HTTP 교환 기록을 반환하고, 호출 전이면 ``None``을 반환합니다."""

        return self._exchanges[-1] if self._exchanges else None

    def clear_exchanges(self) -> None:
        """디버그 실행 단위를 나누기 위해 누적 HTTP 교환 기록을 비웁니다."""

        self._exchanges.clear()

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
        url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        request_params = self._params(
            params,
            service_key_param=service_key_param,
            format_param=format_param,
            format_value=format_value,
        )
        response = self._request(
            url,
            request_params,
        )
        try:
            payload = response.json()
        except ValueError as exc:
            self._record_exchange(
                url=url,
                request_params=request_params,
                response=response,
                response_text=response.text[:300],
            )
            _raise_for_plain_text(response.text)
            raise AirKoreaParseError(f"failed to parse JSON response: {exc}") from exc

        if not isinstance(payload, Mapping):
            self._record_exchange(
                url=url,
                request_params=request_params,
                response=response,
            )
            raise AirKoreaParseError("JSON response root is not an object")

        try:
            body = _extract_body(payload)
        except Exception:
            self._record_exchange(
                url=url,
                request_params=request_params,
                response=response,
                response_json=payload,
            )
            raise

        self._record_exchange(
            url=url,
            request_params=request_params,
            response=response,
            response_body=body,
            response_json=payload,
        )
        return body

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

    def _record_exchange(
        self,
        *,
        url: str,
        request_params: Mapping[str, Any],
        response: ResponseLike,
        response_body: Mapping[str, Any] | None = None,
        response_json: Mapping[str, Any] | None = None,
        response_text: str = "",
    ) -> None:
        self._exchanges.append(
            HttpExchange(
                method="GET",
                url=url,
                request_params=sanitize_request_params(request_params),
                status_code=response.status_code,
                response_headers=_response_headers(response),
                response_body=response_body,
                response_json=response_json,
                response_text=response_text,
            )
        )


def _response_headers(response: ResponseLike) -> dict[str, str]:
    headers = getattr(response, "headers", {})
    if not isinstance(headers, Mapping):
        return {}
    return {str(key): str(value) for key, value in headers.items()}


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

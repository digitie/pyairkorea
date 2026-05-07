"""Public metadata and sanitization helpers for AirKorea responses."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from datetime import datetime
from typing import Any

from pyairkorea.models import AirKoreaCallContext

_CREDENTIAL_PARAM_NAMES = {
    "apikey",
    "api_key",
    "authkey",
    "auth_key",
    "key",
    "servicekey",
    "service_key",
}


def is_credential_param(name: str) -> bool:
    """Return whether a request parameter name usually carries credentials."""

    return name.replace("-", "_").lower() in _CREDENTIAL_PARAM_NAMES


def sanitize_request_params(params: Mapping[str, Any]) -> dict[str, Any]:
    """Return request params with credential-bearing keys removed."""

    sanitized: dict[str, Any] = {}
    for key, value in params.items():
        text_key = str(key)
        if is_credential_param(text_key):
            continue
        sanitized[text_key] = _sanitize_value(value)
    return sanitized


def make_call_context(
    *,
    service_name: str,
    endpoint: str,
    request_params: Mapping[str, Any] | None = None,
    collected_at: datetime | None = None,
    provider: str = "data.go.kr",
) -> AirKoreaCallContext:
    """Build sanitized provenance metadata for an AirKorea response."""

    kwargs: dict[str, Any] = {
        "provider": provider,
        "service_name": service_name,
        "endpoint": endpoint,
        "request_params": sanitize_request_params(request_params or {}),
    }
    if collected_at is not None:
        kwargs["collected_at"] = collected_at
    return AirKoreaCallContext(**kwargs)


def make_cache_key(
    endpoint: str,
    params: Mapping[str, Any] | None = None,
    *,
    service_name: str | None = None,
    namespace: str = "pyairkorea:v1",
) -> str:
    """Return a stable cache key from endpoint and sanitized request inputs."""

    payload = {
        "service_name": service_name,
        "endpoint": endpoint,
        "params": _canonical_jsonable(sanitize_request_params(params or {})),
    }
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
    return f"{namespace}:{digest}"


def _sanitize_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return sanitize_request_params(value)
    if isinstance(value, list):
        return [_sanitize_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_sanitize_value(item) for item in value)
    return value


def _canonical_jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _canonical_jsonable(value[key]) for key in sorted(value, key=str)}
    if isinstance(value, (list, tuple)):
        return [_canonical_jsonable(item) for item in value]
    if isinstance(value, datetime):
        return value.isoformat()
    return value

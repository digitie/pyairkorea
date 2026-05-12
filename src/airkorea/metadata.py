"""AirKorea 응답용 공개 메타데이터와 인증키 제거 헬퍼."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from datetime import datetime
from typing import Any

from airkorea.models import AirKoreaCallContext

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
    """요청 파라미터 이름이 보통 인증 정보를 담는지 반환합니다."""

    return name.replace("-", "_").lower() in _CREDENTIAL_PARAM_NAMES


def sanitize_request_params(params: Mapping[str, Any]) -> dict[str, Any]:
    """인증 정보가 담긴 key를 제거한 요청 파라미터를 반환합니다."""

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
    """AirKorea 응답의 인증키 제거 출처 메타데이터를 만듭니다."""

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
    namespace: str = "airkorea:v1",
) -> str:
    """endpoint와 인증키 제거 요청 입력으로 안정적인 캐시 키를 반환합니다."""

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

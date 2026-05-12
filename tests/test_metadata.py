from __future__ import annotations

from datetime import datetime, timezone

from airkorea.metadata import (
    is_credential_param,
    make_cache_key,
    make_call_context,
    sanitize_request_params,
)


def test_sanitize_request_params_removes_common_credential_keys() -> None:
    params = {
        "serviceKey": "secret",
        "ServiceKey": "secret2",
        "auth_key": "secret3",
        "pageNo": 1,
        "nested": {"api_key": "secret4", "numOfRows": 10},
    }

    sanitized = sanitize_request_params(params)

    assert is_credential_param("serviceKey")
    assert sanitized == {"pageNo": 1, "nested": {"numOfRows": 10}}


def test_make_call_context_is_sanitized_and_timestamped() -> None:
    collected_at = datetime(2026, 5, 7, tzinfo=timezone.utc)

    context = make_call_context(
        service_name="MsrstnInfoInqireSvc",
        endpoint="getMsrstnList",
        request_params={"serviceKey": "secret", "stationName": "Jongno-gu"},
        collected_at=collected_at,
    )

    assert context.provider == "data.go.kr"
    assert context.service_name == "MsrstnInfoInqireSvc"
    assert context.endpoint == "getMsrstnList"
    assert context.request_params == {"stationName": "Jongno-gu"}
    assert context.collected_at == collected_at


def test_make_cache_key_is_stable_and_ignores_credentials() -> None:
    first = make_cache_key(
        "getMsrstnList",
        {"serviceKey": "secret", "addr": "Seoul"},
        service_name="MsrstnInfoInqireSvc",
    )
    second = make_cache_key(
        "getMsrstnList",
        {"serviceKey": "different", "addr": "Seoul"},
        service_name="MsrstnInfoInqireSvc",
    )

    assert first == second
    assert first.startswith("airkorea:v1:")

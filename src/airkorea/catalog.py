"""AirKorea 지원 API 카탈로그."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ApiCatalogEntry:
    """지원하는 AirKorea endpoint 하나에 대한 사람이 읽기 쉬운 카탈로그 항목."""

    dataset_name: str
    service_label: str
    service_name: str
    base_url: str
    endpoint: str
    method_names: tuple[str, ...]
    portal_url: str
    service_key_url: str
    service_key_param: str = "serviceKey"

    @property
    def url(self) -> str:
        """Base URL과 endpoint를 합친 호출 URL을 반환합니다."""

        return f"{self.base_url.rstrip('/')}/{self.endpoint.lstrip('/')}"

    def to_dict(self) -> dict[str, Any]:
        """Streamlit dataframe/json 표시에 바로 쓸 수 있는 dict를 반환합니다."""

        return {
            "dataset_name": self.dataset_name,
            "service_label": self.service_label,
            "service_name": self.service_name,
            "endpoint": self.endpoint,
            "method_names": list(self.method_names),
            "service_key_param": self.service_key_param,
            "base_url": self.base_url,
            "url": self.url,
            "portal_url": self.portal_url,
            "service_key_url": self.service_key_url,
        }


_SERVICE_INFO: dict[str, dict[str, str]] = {
    "ArpltnInforInqireSvc": {
        "dataset_name": "한국환경공단_에어코리아_대기오염정보",
        "service_label": "대기오염정보",
        "base_url": "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc",
        "portal_url": "https://www.data.go.kr/data/15073861/openapi.do",
        "service_key_param": "serviceKey",
    },
    "MsrstnInfoInqireSvc": {
        "dataset_name": "한국환경공단_에어코리아_측정소정보",
        "service_label": "측정소정보",
        "base_url": "http://apis.data.go.kr/B552584/MsrstnInfoInqireSvc",
        "portal_url": "https://www.data.go.kr/data/15073877/openapi.do",
        "service_key_param": "serviceKey",
    },
    "ArpltnStatsSvc": {
        "dataset_name": "한국환경공단_에어코리아_대기오염통계 현황",
        "service_label": "대기오염통계 현황",
        "base_url": "http://apis.data.go.kr/B552584/ArpltnStatsSvc",
        "portal_url": "https://www.data.go.kr/data/15073855/openapi.do",
        "service_key_param": "serviceKey",
    },
    "OzYlwsndOccrrncInforInqireSvc": {
        "dataset_name": "한국환경공단_에어코리아_오존황사 발생정보",
        "service_label": "오존황사 발생정보",
        "base_url": "http://apis.data.go.kr/B552584/OzYlwsndOccrrncInforInqireSvc",
        "portal_url": "https://www.data.go.kr/data/15073872/openapi.do",
        "service_key_param": "serviceKey",
    },
    "UlfptcaAlarmInqireSvc": {
        "dataset_name": "한국환경공단_에어코리아_미세먼지 경보 발령 현황",
        "service_label": "미세먼지 경보 발령 현황",
        "base_url": "http://apis.data.go.kr/B552584/UlfptcaAlarmInqireSvc",
        "portal_url": "https://www.data.go.kr/data/15073885/openapi.do",
        "service_key_param": "serviceKey",
    },
    "UserSportSvc": {
        "dataset_name": "한국환경공단_에어코리아_사용자 지원",
        "service_label": "사용자 지원",
        "base_url": "http://apis.data.go.kr/B552584/UserSportSvc",
        "portal_url": "https://www.data.go.kr/data/15075624/openapi.do",
        "service_key_param": "ServiceKey",
    },
    "MinuDustFrcstDspthSvc": {
        "dataset_name": "한국환경공단_에어코리아_고농도 초미세먼지(50초과) 예보 정보",
        "service_label": "고농도 초미세먼지(50초과) 예보 정보",
        "base_url": "http://apis.data.go.kr/B552584/MinuDustFrcstDspthSvc",
        "portal_url": "https://www.data.go.kr/data/15112307/openapi.do",
        "service_key_param": "serviceKey",
    },
    "RltmKhaiInfoSvc": {
        "dataset_name": "한국환경공단_에어코리아_통합대기환경지수(CAI) 조회 서비스",
        "service_label": "통합대기환경지수(CAI) 조회 서비스",
        "base_url": "http://apis.data.go.kr/B552584/RltmKhaiInfoSvc",
        "portal_url": "https://www.data.go.kr/data/15140253/openapi.do",
        "service_key_param": "serviceKey",
    },
    "arpltsNtnBkgrDnstSyrdt": {
        "dataset_name": "한국환경공단_대기오염물질 국가배경농도 합성데이터 조회 서비스",
        "service_label": "국가배경농도 합성데이터 조회 서비스",
        "base_url": "http://apis.data.go.kr/B552584/arpltsNtnBkgrDnstSyrdt",
        "portal_url": "https://www.data.go.kr/data/15153593/openapi.do",
        "service_key_param": "serviceKey",
    },
    "atmstMsrstnRltmInfo": {
        "dataset_name": "한국환경공단_에어코리아 측정소별 실시간 측정정보 영문 조회 서비스",
        "service_label": "측정소별 실시간 측정정보 영문 조회 서비스",
        "base_url": "http://apis.data.go.kr/B552584/atmstMsrstnRltmInfo",
        "portal_url": "https://www.data.go.kr/data/15156659/openapi.do",
        "service_key_param": "serviceKey",
    },
    "atmstMsrstnInfoEngNm": {
        "dataset_name": "한국환경공단_에어코리아_측정소 영문 정보 조회 서비스",
        "service_label": "측정소 영문 정보 조회 서비스",
        "base_url": "http://apis.data.go.kr/B552584/atmstMsrstnInfoEngNm",
        "portal_url": "https://www.data.go.kr/data/15156708/openapi.do",
        "service_key_param": "serviceKey",
    },
}

_ENDPOINT_METHODS: dict[tuple[str, str], tuple[str, ...]] = {
    ("ArpltnInforInqireSvc", "getMsrstnAcctoRltmMesureDnsty"): (
        "station_measurements",
        "latest_station_measurement",
        "measurement_near",
    ),
    ("ArpltnInforInqireSvc", "getUnityAirEnvrnIdexSnstiveAboveMsrstnList"): (
        "unhealthy_stations",
    ),
    ("ArpltnInforInqireSvc", "getCtprvnRltmMesureDnsty"): ("sido_measurements",),
    ("ArpltnInforInqireSvc", "getMinuDustFrcstDspth"): ("forecast_notices",),
    ("ArpltnInforInqireSvc", "getMinuDustWeekFrcstDspth"): ("weekly_forecasts",),
    ("MsrstnInfoInqireSvc", "getMsrstnList"): ("stations",),
    ("MsrstnInfoInqireSvc", "getNearbyMsrstnList"): ("nearby_stations", "measurement_near"),
    ("MsrstnInfoInqireSvc", "getTMStdrCrdnt"): ("tm_coordinates",),
    ("ArpltnStatsSvc", "getCtprvnMesureLIst"): ("sido_average_stats",),
    ("ArpltnStatsSvc", "getCtprvnMesureSidoLIst"): ("city_average_stats",),
    ("ArpltnStatsSvc", "getMsrstnAcctoRDyrg"): ("station_daily_stats",),
    ("ArpltnStatsSvc", "getMsrstnAcctoRMmrg"): ("station_monthly_stats",),
    ("OzYlwsndOccrrncInforInqireSvc", "getOzAdvsryOccrrncInfo"): ("ozone_advisories",),
    ("OzYlwsndOccrrncInforInqireSvc", "getYlwsndAdvsryOccrrncInfo"): (
        "yellow_dust_advisories",
    ),
    ("UlfptcaAlarmInqireSvc", "getUlfptcaAlarmInfo"): ("dust_alarms",),
    ("UserSportSvc", "getSvckeyDalyStats"): ("traffic_stats",),
    ("MinuDustFrcstDspthSvc", "getMinuDustFrcstDspth50Over"): (
        "high_pm25_forecasts",
    ),
    ("RltmKhaiInfoSvc", "getMsrstnKhaiRltmDnsty"): ("cai_measurements",),
    ("arpltsNtnBkgrDnstSyrdt", "getList"): ("background_concentrations",),
    ("atmstMsrstnRltmInfo", "getList"): ("english_measurements",),
    ("atmstMsrstnInfoEngNm", "getList"): ("english_stations",),
}

_CATALOG = tuple(
    ApiCatalogEntry(
        dataset_name=_SERVICE_INFO[service_name]["dataset_name"],
        service_label=_SERVICE_INFO[service_name]["service_label"],
        service_name=service_name,
        base_url=_SERVICE_INFO[service_name]["base_url"],
        endpoint=endpoint,
        method_names=method_names,
        portal_url=_SERVICE_INFO[service_name]["portal_url"],
        service_key_url=_SERVICE_INFO[service_name]["portal_url"],
        service_key_param=_SERVICE_INFO[service_name]["service_key_param"],
    )
    for (service_name, endpoint), method_names in _ENDPOINT_METHODS.items()
)

_CATALOG_BY_ENDPOINT = {
    (entry.service_name, entry.endpoint): entry for entry in _CATALOG
}


def api_catalog() -> tuple[ApiCatalogEntry, ...]:
    """지원 endpoint 전체 카탈로그를 반환합니다."""

    return _CATALOG


def api_catalog_dicts() -> list[dict[str, Any]]:
    """Streamlit dataframe 등에 바로 넘길 수 있는 dict 카탈로그를 반환합니다."""

    return [entry.to_dict() for entry in _CATALOG]


def get_api_catalog_entry(service_name: str, endpoint: str) -> ApiCatalogEntry:
    """서비스명과 endpoint에 맞는 카탈로그 항목을 반환합니다."""

    canonical_service_name = canonical_service_name_for_catalog(service_name)
    try:
        return _CATALOG_BY_ENDPOINT[(canonical_service_name, endpoint)]
    except KeyError as exc:
        known = ", ".join(
            entry.endpoint for entry in _CATALOG if entry.service_name == canonical_service_name
        )
        raise ValueError(
            f"{canonical_service_name} does not support endpoint {endpoint!r}; known: {known}"
        ) from exc


def api_catalog_for_method(method_name: str) -> tuple[ApiCatalogEntry, ...]:
    """public method 이름과 연결된 카탈로그 항목을 반환합니다."""

    return tuple(entry for entry in _CATALOG if method_name in entry.method_names)


def api_catalog_for_debug_input(
    function_name: str,
    input_data: Mapping[str, Any] | None = None,
) -> tuple[ApiCatalogEntry, ...]:
    """디버그 실행 입력으로 Streamlit Trace 탭에 보여줄 카탈로그 항목을 찾습니다."""

    if function_name == "call":
        data = input_data or {}
        service_name = data.get("service_name")
        endpoint = data.get("endpoint")
        if isinstance(service_name, str) and isinstance(endpoint, str):
            return (get_api_catalog_entry(service_name, endpoint),)
        return ()
    return api_catalog_for_method(function_name)


def canonical_service_name_for_catalog(service_name: str) -> str:
    """대소문자를 정규화한 AirKorea 서비스명을 반환합니다."""

    if service_name in _SERVICE_INFO:
        return service_name
    lookup = {name.lower(): name for name in _SERVICE_INFO}
    try:
        return lookup[service_name.lower()]
    except KeyError as exc:
        known = ", ".join(_SERVICE_INFO)
        raise ValueError(f"unknown AirKorea service {service_name!r}; known: {known}") from exc


__all__ = [
    "ApiCatalogEntry",
    "api_catalog",
    "api_catalog_dicts",
    "api_catalog_for_debug_input",
    "api_catalog_for_method",
    "canonical_service_name_for_catalog",
    "get_api_catalog_entry",
]

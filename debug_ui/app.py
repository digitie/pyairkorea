"""AirKorea fixture 디버그 UI."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from airkorea import (  # noqa: E402
    AirKoreaClient,
    __version__,
    api_catalog_dicts,
    jsonable,
    load_service_key,
    normalize_service_key,
    run_debug_method,
    save_debug_fixture,
)
from airkorea.debug import DEBUGGABLE_METHODS  # noqa: E402

SIDO_OPTIONS = [
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
]


def main() -> None:
    st.set_page_config(page_title="AirKorea Debug UI", layout="wide")
    st.title("AirKorea Debug UI")

    catalog_rows = api_catalog_dicts()
    method_options = _method_options(catalog_rows)

    with st.sidebar:
        st.subheader("API")
        selected_function = st.selectbox("API", method_options)
        selected_catalog = _catalog_for_method(catalog_rows, selected_function)
        st.caption("API full name")
        st.write(_api_full_name(selected_function, selected_catalog))
        st.caption(_api_description(selected_function, selected_catalog))

        loaded_key = load_service_key()
        st.subheader("Environment")
        environment = st.selectbox(
            "Environment",
            ["env", "manual"],
            index=0 if loaded_key else 1,
        )

        st.subheader("Auth")
        if environment == "manual":
            service_key_input = st.text_input(
                "serviceKey",
                value="",
                type="password",
                placeholder="직접 입력",
                help="DATA_GO_KR_SERVICE_KEY 환경변수 또는 .env 값도 사용할 수 있습니다.",
            )
            effective_service_key = service_key_input
        else:
            effective_service_key = loaded_key
            if loaded_key:
                st.caption("DATA_GO_KR_SERVICE_KEY 값을 사용합니다. Source: process env 또는 .env")
            else:
                st.warning("DATA_GO_KR_SERVICE_KEY 값을 찾지 못했습니다.")
        _service_key_links(selected_catalog)

        timeout = st.number_input("Timeout", min_value=1.0, max_value=60.0, value=10.0)
        fixture_base_dir = _fixture_base_dir_sidebar()

    tabs = st.tabs(
        [
            "Raw Response",
            "Pydantic Model",
            "Processed Result",
            "Validation Errors",
            "Debug Trace",
            "Fixture / Testcase",
        ]
    )

    with tabs[0]:
        _raw_response_tab(
            selected_function,
            selected_catalog,
            catalog_rows,
            effective_service_key,
            float(timeout),
        )
    with tabs[1]:
        _pydantic_model_tab(selected_function)
    with tabs[2]:
        _processed_result_tab(selected_function)
    with tabs[3]:
        _validation_errors_tab(selected_function)
    with tabs[4]:
        _debug_trace_tab(catalog_rows, selected_function, selected_catalog)
    with tabs[5]:
        _fixture_tab(_current_debug_run(selected_function), fixture_base_dir)


def _run(
    selected_function: str,
    input_data: dict[str, Any],
    service_key: str | None,
    timeout: float,
) -> None:
    normalized_key = normalize_service_key(service_key or "")
    if not normalized_key:
        st.session_state.pop("debug_run", None)
        st.error("서비스키가 필요합니다. 환경변수, .env, 또는 사이드바 입력을 확인하세요.")
        return

    client = AirKoreaClient(
        normalized_key,
        timeout=timeout,
        retries=0,
    )
    st.session_state.debug_run = run_debug_method(client, selected_function, input_data)


def _raw_response_tab(
    selected_function: str,
    selected_catalog: list[dict[str, Any]],
    catalog_rows: list[dict[str, Any]],
    service_key: str | None,
    timeout: float,
) -> None:
    st.subheader(_selected_dataset_name(selected_function, selected_catalog))
    st.caption(_api_full_name(selected_function, selected_catalog))

    try:
        submitted, input_data, missing = _request_form(selected_function, catalog_rows)
    except ValueError as exc:
        st.error(str(exc))
        return

    if selected_function == "call":
        _service_key_links(_call_catalog_for_input(input_data, catalog_rows))

    st.subheader("Request params preview")
    st.json(input_data)

    if submitted:
        if missing:
            st.error("필수 파라미터를 입력하세요: " + ", ".join(missing))
        else:
            _run(selected_function, input_data, service_key, timeout)

    debug_run = _current_debug_run(selected_function)
    if debug_run is None:
        st.info("Run selected API를 누르면 raw response를 확인합니다.")
        return

    if debug_run.error:
        st.error(debug_run.error.get("message") or "API 실행 중 오류가 발생했습니다.")
    st.json(debug_run.response)


def _request_form(
    selected_function: str,
    catalog_rows: list[dict[str, Any]],
) -> tuple[bool, dict[str, Any], list[str]]:
    key_prefix = f"request:{selected_function}"

    with st.form(f"request-form:{selected_function}"):
        if selected_function == "call":
            st.subheader("Required parameters")
            required_specs: list[dict[str, Any]] = []
            form_input = _call_input_form(catalog_rows)
        else:
            specs = _parameter_specs(selected_function)
            required_specs = [spec for spec in specs if spec.get("required")]
            optional_specs = [spec for spec in specs if not spec.get("required")]
            form_input = {}

            st.subheader("Required parameters")
            if required_specs:
                form_input.update(_render_specs(selected_function, required_specs))
            else:
                st.caption("이 API는 라이브러리 호출 기준의 필수 파라미터가 없습니다.")

            st.subheader("Optional parameters")
            form_input.update(_render_specs(selected_function, optional_specs))

        extra_text = st.text_area(
            "Extra kwargs JSON",
            value="{}",
            height=110,
            help="폼에 없는 라이브러리 kwargs를 JSON object로 추가하거나 같은 key를 덮어씁니다.",
            key=f"{key_prefix}:extra",
        )
        submitted = st.form_submit_button("Run selected API")

    extra_params = _parse_extra_params(extra_text)
    input_data = {**form_input, **extra_params}
    missing = [
        spec["name"]
        for spec in required_specs
        if not str(input_data.get(spec["name"], "")).strip()
    ]
    return submitted, input_data, missing


def _parse_extra_params(text: str) -> dict[str, Any]:
    if not text.strip():
        return {}
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Extra kwargs JSON 오류: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ValueError("Extra kwargs JSON은 object여야 합니다.")
    return parsed


def _current_debug_run(selected_function: str) -> Any | None:
    debug_run = st.session_state.get("debug_run")
    if debug_run is None:
        return None
    if getattr(debug_run, "function", None) != selected_function:
        return None
    return debug_run


def _fixture_tab(debug_run: Any, fixture_base_dir: str) -> None:
    if debug_run is None:
        st.info("실행 후 fixture로 저장할 수 있습니다.")
        st.caption("Fixture base dir")
        st.code(fixture_base_dir, language=None)
        return

    with st.form("fixture_form"):
        case_name = st.text_input("Case name", value=f"{debug_run.function}_case")
        description = st.text_area("Description", value="")
        assertion_mode = st.selectbox(
            "Assertion mode",
            ["snapshot", "schema_only", "required_fields", "count"],
        )
        exclude_fields = st.text_input(
            "Exclude fields",
            value="fetched_at, request_id, updated_at, collected_at",
        )
        required_fields = st.text_input("Required fields", value="")
        base_dir = st.text_input("Fixture base dir", value=fixture_base_dir)
        overwrite = st.checkbox("Overwrite existing fixture", value=False)
        submitted = st.form_submit_button("Save as fixture")

    if not submitted:
        return

    assertion = {
        "mode": assertion_mode,
        "exclude_fields": [item.strip() for item in exclude_fields.split(",") if item.strip()],
        "required_fields": [item.strip() for item in required_fields.split(",") if item.strip()],
    }
    try:
        path = save_debug_fixture(
            base_dir=base_dir,
            case_name=case_name,
            description=description,
            assertion=assertion,
            library_version=__version__,
            overwrite=overwrite,
            debug_run=debug_run,
        )
    except Exception as exc:
        st.error(str(exc))
    else:
        st.success(f"Saved: {path}")


def _pydantic_model_tab(selected_function: str) -> None:
    debug_run = _current_debug_run(selected_function)
    if debug_run is None:
        st.info("Raw Response 탭에서 선택한 API를 실행하면 여기에서 Pydantic 모델을 확인합니다.")
        return
    if debug_run.error:
        st.warning("API 실행 중 오류가 있어 parsed model이 비어 있을 수 있습니다.")
    st.json(jsonable(debug_run.parsed) if debug_run.parsed is not None else {})


def _processed_result_tab(selected_function: str) -> None:
    debug_run = _current_debug_run(selected_function)
    if debug_run is None:
        st.info("Raw Response 탭에서 API를 실행하면 처리된 row preview를 표시합니다.")
        return

    processed = jsonable(debug_run.processed)
    rows = _table_rows(processed)
    if rows:
        st.dataframe(rows, width="stretch", hide_index=True)
    else:
        st.json(processed if processed is not None else {})


def _validation_errors_tab(selected_function: str) -> None:
    debug_run = _current_debug_run(selected_function)
    if debug_run is None:
        st.info("아직 실행된 API가 없습니다.")
        return
    if debug_run.error:
        st.json(debug_run.error)
        return
    st.success("오류 없이 실행됐습니다.")


def _debug_trace_tab(
    catalog_rows: list[dict[str, Any]],
    selected_function: str,
    selected_catalog: list[dict[str, Any]],
) -> None:
    debug_run = _current_debug_run(selected_function)

    st.subheader("Catalog")
    st.dataframe(catalog_rows, width="stretch", hide_index=True)

    st.subheader("Selected API")
    if selected_function == "call":
        selected_rows = list(debug_run.catalog) if debug_run and debug_run.catalog else []
        if selected_rows:
            st.json(selected_rows[0] if len(selected_rows) == 1 else selected_rows)
            _service_key_links(selected_rows)
        else:
            st.info(
                "Raw Response 탭에서 service와 endpoint를 선택해 실행하면 "
                "선택 API를 표시합니다."
            )
    else:
        st.json(selected_catalog[0] if len(selected_catalog) == 1 else selected_catalog)
        _service_key_links(selected_catalog)
    st.caption("credential env: DATA_GO_KR_SERVICE_KEY")

    st.subheader("Trace")
    if debug_run:
        st.code("\n".join(debug_run.trace) or "trace 없음")
    else:
        st.info("아직 실행 trace가 없습니다.")


def _render_specs(
    method_name: str,
    specs: list[dict[str, Any]],
) -> dict[str, Any]:
    values: dict[str, Any] = {}
    if not specs:
        st.caption("해당 파라미터가 없습니다.")
        return values

    columns = st.columns(2)
    for index, spec in enumerate(specs):
        with columns[index % 2]:
            value = _param_widget(method_name, spec)
            if value is not None and value != "":
                values[spec["name"]] = value
    return values


def _param_widget(
    method_name: str,
    spec: dict[str, Any],
) -> Any:
    key = f"param_{method_name}_{spec['name']}"
    label = spec["label"]
    help_text = spec.get("help")
    kind = spec.get("kind", "text")
    default = spec.get("default")

    if kind == "select":
        options = spec["options"]
        index = options.index(default) if default in options else 0
        value = st.selectbox(
            label,
            options,
            index=index,
            key=key,
            help=help_text,
        )
        return None if value == "" else value

    if kind == "int":
        return int(
            st.number_input(
                label,
                min_value=spec.get("min_value", 1),
                value=int(default if default is not None else spec.get("min_value", 1)),
                step=1,
                key=key,
                help=help_text,
            )
        )

    if kind == "float":
        return float(
            st.number_input(
                label,
                value=float(default if default is not None else 0.0),
                key=key,
                help=help_text,
            )
        )

    if kind == "json":
        text = st.text_area(
            label,
            value=json.dumps(default or {}, ensure_ascii=False, indent=2),
            key=key,
            help=help_text,
        )
        if not text.strip():
            return None
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            st.error(f"{label} JSON 오류: {exc}")
            return None

    return st.text_input(
        label,
        value=str(default or ""),
        key=key,
        help=help_text,
    ).strip()


def _call_input_form(catalog_rows: list[dict[str, Any]]) -> dict[str, Any]:
    service_names = sorted({row["service_name"] for row in catalog_rows})
    service_name = st.selectbox(
        "Service name",
        service_names,
        key="param_call_service_name",
        help="SUPPORTED_ENDPOINTS의 AirKorea 서비스명",
    )
    endpoint_rows = [row for row in catalog_rows if row["service_name"] == service_name]
    endpoints = [row["endpoint"] for row in endpoint_rows]
    endpoint = st.selectbox(
        "Endpoint",
        endpoints,
        key="param_call_endpoint",
        help="공식 endpoint 철자",
    )
    selected_row = next(row for row in endpoint_rows if row["endpoint"] == endpoint)
    st.caption(f"데이터셋: {selected_row['dataset_name']}")

    st.subheader("Optional parameters")
    params_text = st.text_area(
        "params",
        value=json.dumps(_default_call_params(endpoint), ensure_ascii=False, indent=2),
        key="param_call_params",
        help="endpoint별 query parameter object",
    )
    params: dict[str, Any] = {}
    if params_text.strip():
        try:
            parsed = json.loads(params_text)
        except json.JSONDecodeError as exc:
            st.error(f"params JSON 오류: {exc}")
        else:
            if isinstance(parsed, dict):
                params = parsed
            else:
                st.error("params는 JSON object여야 합니다.")

    col1, col2 = st.columns(2)
    with col1:
        page_no = st.number_input(
            "page_no",
            min_value=1,
            value=1,
            step=1,
            key="param_call_page_no",
        )
    with col2:
        num_of_rows = st.number_input(
            "num_of_rows",
            min_value=1,
            value=5,
            step=1,
            key="param_call_num_of_rows",
        )

    return {
        "service_name": service_name,
        "endpoint": endpoint,
        "params": params,
        "page_no": int(page_no),
        "num_of_rows": int(num_of_rows),
    }


def _table_rows(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list) and all(isinstance(item, dict) for item in value):
        return value
    if isinstance(value, dict):
        items = value.get("items")
        if isinstance(items, list) and all(isinstance(item, dict) for item in items):
            return items
        raw_items = value.get("raw", {}).get("body", {}).get("items")
        if isinstance(raw_items, list) and all(isinstance(item, dict) for item in raw_items):
            return raw_items
    return []


def _fixture_base_dir_sidebar() -> str:
    st.subheader("Fixtures")
    candidates = _fixture_dir_candidates()
    options = [str(path) for path in candidates]
    custom_label = "Custom..."
    selected = st.selectbox("Fixture base dir", [*options, custom_label])
    if selected == custom_label:
        selected = st.text_input(
            "Custom fixture base dir",
            value=str((ROOT / "tests" / "fixtures").resolve()),
        )
    st.caption(selected)
    return selected


def _fixture_dir_candidates() -> list[Path]:
    preferred = [
        ROOT / "tests" / "fixtures",
        ROOT / "tests",
        ROOT / "debug_ui",
        ROOT,
    ]
    candidates: list[Path] = []
    for path in preferred:
        resolved = path.resolve()
        if resolved not in candidates:
            candidates.append(resolved)
    return candidates


def _selected_dataset_name(
    selected_function: str,
    selected_catalog: list[dict[str, Any]],
) -> str:
    if selected_function == "call":
        return "AirKorea raw call"
    dataset_names = sorted(
        {
            str(row["dataset_name"])
            for row in selected_catalog
            if row.get("dataset_name")
        }
    )
    if len(dataset_names) == 1:
        return dataset_names[0]
    if dataset_names:
        return f"{selected_function} ({len(dataset_names)} datasets)"
    return selected_function


def _api_full_name(selected_function: str, catalog_rows: list[dict[str, Any]]) -> str:
    if selected_function == "call":
        return "AirKoreaClient.call"
    if not catalog_rows:
        return selected_function
    return "\n".join(
        f"{row['dataset_name']} / {row['service_name']} / {row['endpoint']}"
        for row in catalog_rows
    )


def _api_description(selected_function: str, catalog_rows: list[dict[str, Any]]) -> str:
    if selected_function == "call":
        return "service_name과 endpoint를 직접 선택해 AirKorea endpoint를 호출합니다."
    if len(catalog_rows) > 1:
        return (
            f"{selected_function} 함수는 {len(catalog_rows)}개 AirKorea endpoint를 "
            "조합해 호출합니다."
        )
    if catalog_rows:
        row = catalog_rows[0]
        return f"{row['dataset_name']}의 {row['endpoint']} endpoint입니다."
    return f"{selected_function} API입니다."


def _call_catalog_for_input(
    input_data: dict[str, Any],
    catalog_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    service_name = input_data.get("service_name")
    endpoint = input_data.get("endpoint")
    if not isinstance(service_name, str) or not isinstance(endpoint, str):
        return []
    return [
        row
        for row in catalog_rows
        if row["service_name"] == service_name and row["endpoint"] == endpoint
    ]


def _method_options(catalog_rows: list[dict[str, Any]]) -> list[str]:
    methods = {
        method
        for row in catalog_rows
        for method in row["method_names"]
        if method in DEBUGGABLE_METHODS
    }
    methods.add("call")
    return sorted(methods)


def _catalog_for_method(
    catalog_rows: list[dict[str, Any]],
    method_name: str,
) -> list[dict[str, Any]]:
    if method_name == "call":
        return catalog_rows
    return [row for row in catalog_rows if method_name in row["method_names"]]


def _service_key_links(catalog_rows: list[dict[str, Any]]) -> None:
    seen: set[str] = set()
    for row in catalog_rows:
        url = row.get("service_key_url")
        label = row.get("dataset_name") or row.get("service_label") or "서비스키 링크"
        if not isinstance(url, str) or url in seen:
            continue
        seen.add(url)
        st.link_button(f"서비스키 신청/확인: {label}", url)


def _parameter_specs(method_name: str) -> list[dict[str, Any]]:
    common_page = [
        _int_param("page_no", "page_no", default=1, help_text="AirKorea pageNo"),
        _int_param(
            "num_of_rows",
            "num_of_rows",
            default=5,
            help_text="AirKorea numOfRows",
            include=True,
        ),
    ]
    data_term = _select_param(
        "data_term",
        "data_term",
        ["DAILY", "MONTH", "3MONTH"],
        default="DAILY",
    )
    ver = _text_param("ver", "ver", default="1.3")

    specs: dict[str, list[dict[str, Any]]] = {
        "station_measurements": [
            _text_param("station_name", "station_name", required=True, default="종로구"),
            data_term,
            *common_page,
            ver,
        ],
        "latest_station_measurement": [
            _text_param("station_name", "station_name", required=True, default="종로구"),
            data_term,
            ver,
        ],
        "sido_measurements": [
            _select_param("sido_name", "sido_name", SIDO_OPTIONS, required=True, default="서울"),
            *common_page,
            ver,
        ],
        "unhealthy_stations": common_page,
        "forecast_notices": [
            _text_param("search_date", "search_date", help_text="YYYY-MM-DD"),
            _select_param("inform_code", "inform_code", ["", "PM10", "PM25", "O3"]),
            *common_page,
        ],
        "weekly_forecasts": [
            _text_param("search_date", "search_date", help_text="YYYY-MM-DD"),
            *common_page,
        ],
        "stations": [
            _text_param("addr", "addr", default="서울", include=True),
            _text_param("station_name", "station_name"),
            *common_page,
        ],
        "nearby_stations": [
            _float_param("lat", "lat", required=True, default=37.5665),
            _float_param("lon", "lon", required=True, default=126.9780),
            ver,
        ],
        "tm_coordinates": [
            _text_param("umd_name", "umd_name", required=True, default="혜화동"),
            *common_page,
        ],
        "measurement_near": [
            _float_param("lat", "lat", required=True, default=37.5665),
            _float_param("lon", "lon", required=True, default=126.9780),
            data_term,
            ver,
        ],
        "sido_average_stats": [
            _select_param(
                "item_code",
                "item_code",
                ["PM10", "PM25", "O3", "NO2", "CO", "SO2"],
                required=True,
                default="PM25",
            ),
            _select_param("data_gubun", "data_gubun", ["HOUR", "DAILY"], default="HOUR"),
            _select_param(
                "search_condition",
                "search_condition",
                ["WEEK", "MONTH"],
                default="WEEK",
            ),
            *common_page,
        ],
        "city_average_stats": [
            _select_param("sido_name", "sido_name", SIDO_OPTIONS, required=True, default="서울"),
            _select_param("item_code", "item_code", ["", "PM10", "PM25", "O3", "NO2", "CO", "SO2"]),
            _select_param("data_gubun", "data_gubun", ["", "HOUR", "DAILY"]),
            _select_param(
                "search_condition",
                "search_condition",
                ["HOUR", "WEEK", "MONTH"],
                default="HOUR",
            ),
            *common_page,
        ],
        "station_daily_stats": [
            _text_param(
                "inquiry_begin_date",
                "inquiry_begin_date",
                required=True,
                default="2026-04-01",
            ),
            _text_param(
                "inquiry_end_date",
                "inquiry_end_date",
                required=True,
                default="2026-04-30",
            ),
            _text_param("station_name", "station_name"),
            *common_page,
        ],
        "station_monthly_stats": [
            _text_param(
                "inquiry_begin_date",
                "inquiry_begin_date",
                required=True,
                default="2026-04-01",
            ),
            _text_param(
                "inquiry_end_date",
                "inquiry_end_date",
                required=True,
                default="2026-04-30",
            ),
            _text_param("station_name", "station_name"),
            *common_page,
        ],
        "ozone_advisories": [
            _text_param("year", "year", default="2026", include=True),
            *common_page,
        ],
        "yellow_dust_advisories": [
            _text_param("year", "year", default="2026", include=True),
            *common_page,
        ],
        "dust_alarms": [
            _text_param("year", "year", required=True, default="2026"),
            _select_param("item_code", "item_code", ["", "PM10", "PM25"]),
            *common_page,
        ],
        "traffic_stats": [
            _text_param("search_date", "search_date", required=True, default="2026-04-30"),
            *common_page,
        ],
        "high_pm25_forecasts": [
            _text_param("search_date", "search_date", required=True, default="2026-04-30"),
            *common_page,
        ],
        "cai_measurements": [
            _text_param("station_name", "station_name"),
            *common_page,
        ],
        "background_concentrations": [
            _text_param(
                "measurement_date",
                "measurement_date",
                required=True,
                default="2022-01-03",
            ),
            _text_param("station_name", "station_name", required=True, default="s0002"),
            *common_page,
        ],
        "english_measurements": [
            _text_param("station_name", "station_name"),
            *common_page,
        ],
        "english_stations": [
            _text_param("station_name", "station_name"),
            _text_param("road_address", "road_address"),
            *common_page,
        ],
    }
    return specs.get(method_name, [])


def _text_param(
    name: str,
    label: str,
    *,
    required: bool = False,
    default: str = "",
    include: bool = False,
    help_text: str | None = None,
) -> dict[str, Any]:
    return {
        "name": name,
        "label": label,
        "kind": "text",
        "required": required,
        "default": default,
        "include_by_default": include,
        "help": help_text,
    }


def _select_param(
    name: str,
    label: str,
    options: list[str],
    *,
    required: bool = False,
    default: str = "",
) -> dict[str, Any]:
    return {
        "name": name,
        "label": label,
        "kind": "select",
        "required": required,
        "default": default,
        "options": options,
    }


def _int_param(
    name: str,
    label: str,
    *,
    default: int,
    include: bool = False,
    help_text: str | None = None,
) -> dict[str, Any]:
    return {
        "name": name,
        "label": label,
        "kind": "int",
        "required": False,
        "default": default,
        "include_by_default": include,
        "help": help_text,
        "min_value": 1,
    }


def _float_param(
    name: str,
    label: str,
    *,
    required: bool,
    default: float,
) -> dict[str, Any]:
    return {
        "name": name,
        "label": label,
        "kind": "float",
        "required": required,
        "default": default,
    }


def _default_call_params(endpoint: str) -> dict[str, Any]:
    defaults = {
        "getMsrstnList": {"addr": "서울"},
        "getMsrstnAcctoRltmMesureDnsty": {
            "stationName": "종로구",
            "dataTerm": "DAILY",
            "ver": "1.3",
        },
        "getCtprvnRltmMesureDnsty": {"sidoName": "서울", "ver": "1.3"},
        "getNearbyMsrstnList": {"tmX": 198242, "tmY": 451580},
        "getTMStdrCrdnt": {"umdName": "혜화동"},
    }
    return defaults.get(endpoint, {})


def _default_input(method_name: str) -> dict[str, Any]:
    defaults: dict[str, dict[str, Any]] = {
        "station_measurements": {"station_name": "종로구", "num_of_rows": 1},
        "latest_station_measurement": {"station_name": "종로구"},
        "sido_measurements": {"sido_name": "서울", "num_of_rows": 5},
        "stations": {"addr": "서울", "num_of_rows": 5},
        "nearby_stations": {"lat": 37.5665, "lon": 126.9780},
        "forecast_notices": {"num_of_rows": 5},
        "call": {
            "service_name": "MsrstnInfoInqireSvc",
            "endpoint": "getMsrstnList",
            "params": {"addr": "서울"},
            "num_of_rows": 5,
        },
    }
    return defaults.get(method_name, {})


if __name__ == "__main__":
    main()

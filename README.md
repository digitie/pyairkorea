# python-airkorea-api

한국환경공단 AirKorea OpenAPI를 Python에서 쓰기 쉽게 감싼 비공식 클라이언트입니다.

`python-airkorea-api`는 공공데이터포털의 AirKorea 계열 B552584 OpenAPI를 Pydantic v2 기반 Python 객체로 변환합니다. Python import 이름은 `airkorea`입니다. 외부 프로그램에서 안정적으로 붙일 수 있도록 문자열 입력은 계속 지원하면서 enum, 좌표 값 객체, 표준화 helper를 제공합니다.

## 설치

Python 3.10 이상이 필요합니다.

```bash
pip install python-airkorea-api
```

개발 환경:

```bash
pip install -e ".[dev]"
```

## 인증키

공공데이터포털에서 필요한 AirKorea OpenAPI 활용신청을 한 뒤 일반 인증키를 환경변수로 저장합니다.

```bash
export AIRKOREA_SERVICE_KEY="발급받은_인증키"
```

PowerShell:

```powershell
$env:AIRKOREA_SERVICE_KEY="발급받은_인증키"
```

환경변수가 없으면 `AirKoreaClient.from_env()`는 현재 작업 디렉터리의 `.env`에서 같은 이름을 찾습니다.

```dotenv
AIRKOREA_SERVICE_KEY=발급받은_인증키
```

포털에서 키를 복사하면서 앞뒤 공백, 줄바꿈, 탭이 섞여도 클라이언트 생성 시 제거합니다.

## 빠른 사용

```python
from airkorea import AirKoreaClient, DataTerm, SidoName

air = AirKoreaClient.from_env()

latest = air.latest_station_measurement("종로구", data_term=DataTerm.DAILY)
for row in air.sido_measurements(SidoName.SEOUL, num_of_rows=5):
    print(row.station_name, row.pm10_value, row.pm25_value, row.khai_grade_enum)
```

좌표는 `kraddr.base`의 `PlaceCoordinate`를 권장합니다. 기존 `LatLon`, tuple,
mapping, `lat=..., lon=...` 호출도 계속 지원합니다.

```python
from airkorea import PlaceCoordinate

seoul_city_hall = PlaceCoordinate(lat=37.5665, lon=126.9780)
nearby = air.nearby_stations(coordinate=seoul_city_hall)
measurement = air.measurement_near(coordinate=seoul_city_hall)
```

## 라이브러리 친화 API

| 구분 | 제공 타입 |
|---|---|
| 측정 기간 | `DataTerm` |
| 예보 코드 | `InformCode` |
| 오염물질 코드 | `Pollutant` |
| 시도명 | `SidoName` |
| 통계 단위 | `StatsDataGubun`, `StatsSearchCondition` |
| 대기질 등급 | `AirQualityGrade` |
| 위경도 | `PlaceCoordinate` |
| AirKorea TM 좌표 | `TmPoint` |

enum은 `str` 기반이라 기존 문자열 코드와 잘 섞입니다.

```python
from airkorea import Pollutant, StatsDataGubun, StatsSearchCondition

stats = air.sido_average_stats(
    item_code=Pollutant.PM25,
    data_gubun=StatsDataGubun.HOUR,
    search_condition=StatsSearchCondition.WEEK,
)
alarms = air.dust_alarms(2026, item_code=Pollutant.PM10)
```

응답 모델도 외부 프로그램에서 후처리하기 쉽게 enum/좌표 property를 제공합니다.

```python
station = air.stations(station_name="종로구")[0]
print(station.coordinates)        # PlaceCoordinate(...) or None
print(latest.khai_grade_enum)     # AirQualityGrade.MODERATE or None
print(latest.model_dump())        # Pydantic dict
```

원본 endpoint를 직접 호출해야 할 때는 `call()`이 페이지 메타데이터와 인증키가 제거된 호출 context를 함께 반환합니다.

```python
page = air.call(
    "MsrstnInfoInqireSvc",
    "getMsrstnList",
    {"addr": "서울"},
    num_of_rows=10,
)

print(page.items)              # tuple[Mapping[str, Any], ...]
print(page.has_next_page)      # pageNo/numOfRows/totalCount 기반
print(page.request_params)     # serviceKey 제외
```

여러 페이지는 `iter_pages()`로 순회합니다.

```python
for page in air.iter_pages("MsrstnInfoInqireSvc", "getMsrstnList", {"addr": "서울"}):
    for raw_station in page.items:
        print(raw_station["stationName"])
```

캐시 키나 로그용 파라미터가 필요하면 인증키 제거 helper를 사용할 수 있습니다.

```python
from airkorea import make_cache_key, sanitize_request_params

safe_params = sanitize_request_params({"serviceKey": "secret", "addr": "서울"})
cache_key = make_cache_key("getMsrstnList", safe_params, service_name="MsrstnInfoInqireSvc")
```

## API 카탈로그

지원 API 목록은 코드에서 조회할 수 있습니다. 각 항목에는 사람이 읽기 쉬운 데이터셋명, endpoint, Python 메서드, 서비스키 신청 링크가 들어갑니다.

```python
from airkorea import api_catalog_dicts

for row in api_catalog_dicts():
    print(row["dataset_name"], row["endpoint"], row["service_key_url"])
```

## 디버그 fixture

Streamlit 같은 외부 Web UI에서 입력값을 바꿔가며 실행한 결과를 pytest replay fixture로 저장할 수 있도록 `run_debug_method()`와 `save_debug_fixture()`를 제공합니다. 라이브러리 본체는 Streamlit에 의존하지 않습니다.

```python
from airkorea import AirKoreaClient, run_debug_method, save_debug_fixture

air = AirKoreaClient.from_env()
debug_run = run_debug_method(
    air,
    "station_measurements",
    {"station_name": "종로구", "num_of_rows": 1},
)

save_debug_fixture(
    base_dir="tests/fixtures",
    case_name="jongno_normal",
    description="종로구 측정소 실시간 정상 응답",
    debug_run=debug_run,
    library_version="0.4.0",
)
```

Streamlit의 Debug Trace 탭에서는 `debug_run.catalog`를 표나 JSON으로 표시하면 선택한 API의 데이터셋명과 서비스키 링크를 같이 보여줄 수 있습니다.

```python
st.dataframe(debug_run.catalog)
st.code("\n".join(debug_run.trace))
```

fixture 저장 전 인증키성 값은 제거되거나 `<REDACTED>`로 치환됩니다. 저장된 fixture는 `tests/test_generated_fixtures.py`의 공통 runner가 실제 네트워크 없이 replay합니다. 자세한 구조는 [docs/debug-fixtures.md](docs/debug-fixtures.md)를 확인하세요.

자세한 라이브러리 사용 지침은 [docs/library-surface.md](docs/library-surface.md)를 확인하세요.

## 지원 API

| 서비스 | 주요 메서드 |
|---|---|
| 대기오염정보 | `station_measurements`, `sido_measurements`, `unhealthy_stations`, `forecast_notices`, `weekly_forecasts` |
| 측정소정보 | `stations`, `nearby_stations`, `tm_coordinates`, `measurement_near` |
| 대기오염통계 현황 | `sido_average_stats`, `city_average_stats`, `station_daily_stats`, `station_monthly_stats` |
| 오존황사 발생정보 | `ozone_advisories`, `yellow_dust_advisories` |
| 미세먼지 경보 발령 현황 | `dust_alarms` |
| 사용자 지원 | `traffic_stats` |
| 고농도 초미세먼지(50초과) 예보 정보 | `high_pm25_forecasts` |
| 통합대기환경지수(CAI) 조회 | `cai_measurements` |
| 대기오염물질 국가배경농도 합성데이터 | `background_concentrations` |
| 측정소별 실시간 측정정보 영문 조회 | `english_measurements` |
| 측정소 영문 정보 조회 | `english_stations` |

전체 endpoint 목록과 정확한 철자는 [airkorea-api.md](airkorea-api.md)를 확인하세요.

## CLI

CLI는 자주 쓰는 조회를 중심으로 제공합니다. 전체 API는 Python 클라이언트에서 사용할 수 있습니다.

```bash
airkorea station --station-name 종로구
airkorea sido --sido-name 서울 --num-of-rows 25
airkorea stations --addr 서울
airkorea nearby --lat 37.5665 --lon 126.9780
airkorea forecast --search-date 2026-04-30 --inform-code PM10
```

## 개발 검증

```bash
python -m compileall src/airkorea tests
python -m pytest
python -m pytest --cov=airkorea --cov-fail-under=90
python -m ruff check .
python -m mypy src/airkorea
```

실제 API 호출 테스트는 기본 테스트에 넣지 않습니다. 네트워크, 인증키, 실시간 데이터 상태가 흔들리기 때문입니다.

## 문서

- [airkorea-api.md](airkorea-api.md): 공식 API 목록, endpoint, 메서드 매핑
- [docs/library-surface.md](docs/library-surface.md): 외부 프로그램 연동용 타입/좌표 지침
- [docs/debug-fixtures.md](docs/debug-fixtures.md): 디버그 UI fixture 저장과 replay 테스트 구조
- [docs/implementation-status.md](docs/implementation-status.md): 구현/테스트 현황
- [docs/documentation-style.md](docs/documentation-style.md): 문서와 Python 내부 문서 작성 규칙
- [docs/testing.md](docs/testing.md): 테스트 원칙
- [docs/repeated-mistakes.md](docs/repeated-mistakes.md): 반복 실수 방지 로그
- [docs/troubleshooting.md](docs/troubleshooting.md): 오류별 점검표

## 범위

이 패키지는 AirKorea 대기질 API 클라이언트입니다. 한국환경공단의 모든 B552584 서비스(비점오염원, 재활용, 냉매 등)를 포함하지 않습니다.

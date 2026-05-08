# pyairkorea

한국환경공단 AirKorea OpenAPI를 Python에서 쓰기 쉽게 감싼 비공식 클라이언트입니다.

`pyairkorea`는 공공데이터포털의 AirKorea 계열 B552584 OpenAPI를 Pydantic v2 기반 Python 객체로 변환합니다. 외부 프로그램에서 안정적으로 붙일 수 있도록 문자열 입력은 계속 지원하면서 enum, 좌표 값 객체, 표준화 helper를 제공합니다.

## 설치

```bash
pip install pyairkorea
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

## 빠른 사용

```python
from pyairkorea import AirKoreaClient, DataTerm, SidoName

air = AirKoreaClient.from_env()

latest = air.latest_station_measurement("종로구", data_term=DataTerm.DAILY)
for row in air.sido_measurements(SidoName.SEOUL, num_of_rows=5):
    print(row.station_name, row.pm10_value, row.pm25_value, row.khai_grade_enum)
```

좌표는 `LatLon`을 권장합니다. 기존 `lat=..., lon=...` 호출도 계속 지원합니다.

```python
from pyairkorea import LatLon

seoul_city_hall = LatLon(37.5665, 126.9780)
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
| 위경도 | `LatLon` |
| AirKorea TM 좌표 | `TmPoint` |

enum은 `str` 기반이라 기존 문자열 코드와 잘 섞입니다.

```python
from pyairkorea import Pollutant, StatsDataGubun, StatsSearchCondition

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
print(station.coordinates)        # LatLon(...) or None
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
from pyairkorea import make_cache_key, sanitize_request_params

safe_params = sanitize_request_params({"serviceKey": "secret", "addr": "서울"})
cache_key = make_cache_key("getMsrstnList", safe_params, service_name="MsrstnInfoInqireSvc")
```

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
pyairkorea station --station-name 종로구
pyairkorea sido --sido-name 서울 --num-of-rows 25
pyairkorea stations --addr 서울
pyairkorea nearby --lat 37.5665 --lon 126.9780
pyairkorea forecast --search-date 2026-04-30 --inform-code PM10
```

## 개발 검증

```bash
python -m compileall pyairkorea tests
python -m pytest
python -m pytest --cov=pyairkorea --cov-fail-under=90
python -m ruff check .
python -m mypy pyairkorea
```

실제 API 호출 테스트는 기본 테스트에 넣지 않습니다. 네트워크, 인증키, 실시간 데이터 상태가 흔들리기 때문입니다.

## 문서

- [airkorea-api.md](airkorea-api.md): 공식 API 목록, endpoint, 메서드 매핑
- [docs/library-surface.md](docs/library-surface.md): 외부 프로그램 연동용 타입/좌표 지침
- [docs/implementation-status.md](docs/implementation-status.md): 구현/테스트 현황
- [docs/documentation-style.md](docs/documentation-style.md): 문서와 Python 내부 문서 작성 규칙
- [docs/testing.md](docs/testing.md): 테스트 원칙
- [docs/repeated-mistakes.md](docs/repeated-mistakes.md): 반복 실수 방지 로그
- [docs/troubleshooting.md](docs/troubleshooting.md): 오류별 점검표

## 범위

이 패키지는 AirKorea 대기질 API 클라이언트입니다. 한국환경공단의 모든 B552584 서비스(비점오염원, 재활용, 냉매 등)를 포함하지 않습니다.

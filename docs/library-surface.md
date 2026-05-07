# 라이브러리 표면 설계

외부 프로그램에서 `pyairkorea`를 안정적으로 사용하기 위한 public 타입과 좌표 규칙입니다.

## 문자열 호환 enum

기존 문자열 기반 코드는 계속 동작합니다. 새 코드에서는 enum 사용을 권장합니다.

| enum | 용도 | 예시 |
|---|---|---|
| `DataTerm` | 측정소 실시간 측정정보 조회 기간 | `DataTerm.DAILY` |
| `InformCode` | 예보 통보 코드 | `InformCode.PM10` |
| `Pollutant` | 오염물질/item code | `Pollutant.PM25` |
| `SidoName` | 시도명 | `SidoName.SEOUL` |
| `StatsDataGubun` | 통계 집계 단위 | `StatsDataGubun.HOUR` |
| `StatsSearchCondition` | 통계 조회 조건 | `StatsSearchCondition.WEEK` |
| `AirQualityGrade` | 대기질 등급 | `AirQualityGrade.MODERATE` |

```python
from pyairkorea import AirKoreaClient, Pollutant, SidoName

air = AirKoreaClient.from_env()
rows = air.sido_measurements(SidoName.SEOUL)
alarms = air.dust_alarms(2026, item_code=Pollutant.PM25)
```

## 좌표 표준

위경도는 항상 WGS84 `lat, lon` 순서입니다. AirKorea TM 좌표는 `tm_x, tm_y` 순서입니다.

| 타입 | 의미 | 순서 |
|---|---|---|
| `LatLon` | WGS84 위경도 | `lat, lon` |
| `TmPoint` | AirKorea TM 좌표 | `tm_x, tm_y` |

권장:

```python
from pyairkorea import LatLon

point = LatLon(37.5665, 126.9780)
nearby = air.nearby_stations(coordinate=point)
```

호환 입력:

```python
air.nearby_stations(lat=37.5665, lon=126.9780)
air.nearby_stations(coordinate=(37.5665, 126.9780))
air.nearby_stations(coordinate={"latitude": 37.5665, "longitude": 126.9780})
air.nearby_stations(tm={"tmX": 198242, "tmY": 451580})
```

`coordinate`와 `tm` 계열 입력을 동시에 넘기면 `ValueError`가 발생합니다. 좌표계가 섞였을 때 조용히 틀린 측정소를 고르는 일을 막기 위한 의도적인 동작입니다.

## Pydantic 응답 모델

응답 객체는 Pydantic v2 `BaseModel` 기반입니다. 필드 접근은 속성으로 하고, 외부 직렬화에는 `model_dump()`나 `model_dump_json()`을 사용할 수 있습니다. 원본 응답은 `raw`에 보존합니다.

```python
latest = air.latest_station_measurement("종로구")
if latest is not None:
    print(latest.khai_grade_enum)
    print(latest.khai_grade_enum.label if latest.khai_grade_enum else None)
    print(latest.model_dump(mode="json"))

station = air.stations(station_name="종로구")[0]
print(station.coordinates)
```

대표 property:

- `AirQualityMeasurement.khai_grade_enum`
- `CaiMeasurement.khai_grade_enum`
- `EnglishAirQualityMeasurement.khai_grade_enum`
- `ForecastNotice.inform_code_enum`
- `AirQualityStat.item_code_enum`
- `DustAlarm.item_code_enum`
- `Station.coordinates`
- `EnglishStation.coordinates`

## Raw page와 페이지 순회

일반적인 사용은 typed convenience method(`stations()`, `sido_measurements()` 등)를 권장합니다. 아직 typed model이 충분하지 않거나, 응답의 `pageNo`/`numOfRows`/`totalCount` 같은 원본 페이지 메타데이터가 필요하면 `AirKoreaClient.call()`을 사용합니다.

```python
page = air.call(
    "MsrstnInfoInqireSvc",
    "getMsrstnList",
    {"addr": "서울"},
    num_of_rows=10,
)

page.items          # tuple[RawRecord, ...]
page.raw            # response.body 원본 mapping
page.has_next_page  # pageNo/numOfRows/totalCount 기반
page.next_page_no   # 다음 pageNo 또는 None
page.context        # AirKoreaCallContext
```

`call()`은 `SUPPORTED_ENDPOINTS`에 등록된 서비스/endpoint만 호출합니다. 서비스명은 대소문자 차이를 허용하지만 endpoint 철자는 공식 철자를 그대로 요구합니다. 특히 `getCtprvnMesureLIst`, `getCtprvnMesureSidoLIst`, `getMsrstnAcctoRMmrg`는 문서 철자를 유지합니다.

여러 페이지를 가져올 때는 `iter_pages()`를 사용합니다.

```python
for page in air.iter_pages(
    "MsrstnInfoInqireSvc",
    "getMsrstnList",
    {"addr": "서울"},
    num_of_rows=100,
    max_pages=5,
):
    for row in page.items:
        print(row["stationName"])
```

모듈 수준 helper도 공개 API입니다.

- `has_next_page(body)`
- `next_page_no(body)`
- `iter_paginated_pages(fetch_page, ...)`

## Call context와 캐시 키

`AirKoreaCallContext.request_params`는 `serviceKey`, `ServiceKey`, `api_key`, `auth_key` 같은 인증키성 파라미터를 저장하지 않습니다. 로그, 캐시 키, fixture metadata에 그대로 써도 키가 남지 않도록 보수적으로 제거합니다.

```python
from pyairkorea import make_cache_key, sanitize_request_params

safe_params = sanitize_request_params({"serviceKey": "secret", "addr": "서울"})
cache_key = make_cache_key("getMsrstnList", safe_params, service_name="MsrstnInfoInqireSvc")
```

## 정규화 helper

외부 프로그램에서 사용자 입력을 먼저 검증하고 싶다면 helper를 직접 사용할 수 있습니다.

```python
from pyairkorea.codes import normalize_pollutant_code, validate_sido_name
from pyairkorea.coords import coerce_latlon

item_code = normalize_pollutant_code("pm2.5")
sido_name = validate_sido_name("서울")
point = coerce_latlon({"lat": "37.5665", "lon": "126.9780"})
```

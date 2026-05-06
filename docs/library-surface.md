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

## 응답 모델 property

응답 dataclass는 원본 값과 함께 후처리용 property를 제공합니다.

```python
latest = air.latest_station_measurement("종로구")
if latest is not None:
    print(latest.khai_grade_enum)
    print(latest.khai_grade_enum.label if latest.khai_grade_enum else None)

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

## 정규화 helper

외부 프로그램에서 사용자 입력을 먼저 검증하고 싶다면 helper를 직접 사용할 수 있습니다.

```python
from pyairkorea.codes import normalize_pollutant_code, validate_sido_name
from pyairkorea.coords import coerce_latlon

item_code = normalize_pollutant_code("pm2.5")
sido_name = validate_sido_name("서울")
point = coerce_latlon({"lat": "37.5665", "lon": "126.9780"})
```

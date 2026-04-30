# pyairkorea Implementation Status

이 문서는 현재 구현 상태, 검증 방법, 다음 작업자가 반복하지 말아야 할 판단을 한곳에 모읍니다.

## 현재 범위

`AirKoreaClient`는 공공데이터포털의 AirKorea OpenAPI 2개 서비스군을 0.1.0 범위로 구현합니다.

| Method | Endpoint | Status | Notes |
|---|---|---|---|
| `station_measurements()` | `getMsrstnAcctoRltmMesureDnsty` | Implemented | 측정소별 실시간 측정정보 |
| `latest_station_measurement()` | `getMsrstnAcctoRltmMesureDnsty` | Implemented | 최신 1건 편의 메서드 |
| `sido_measurements()` | `getCtprvnRltmMesureDnsty` | Implemented | 시도명 사전 검증 |
| `unhealthy_stations()` | `getUnityAirEnvrnIdexSnstiveAboveMsrstnList` | Implemented | 같은 measurement 모델 사용 |
| `forecast_notices()` | `getMinuDustFrcstDspth` | Implemented | PM10/PM25/O3 예보통보 |
| `weekly_forecasts()` | `getMinuDustWeekFrcstDspth` | Implemented | 주간 초미세먼지 예보 |
| `stations()` | `getMsrstnList` | Implemented | `dmX -> lat`, `dmY -> lon` |
| `nearby_stations()` | `getNearbyMsrstnList` | Implemented | TM 또는 WGS84 입력 |
| `tm_coordinates()` | `getTMStdrCrdnt` | Implemented | 읍면동 기준 TM 좌표 |
| `measurement_near()` | combined | Implemented | 근접 측정소 탐색 후 최신 측정값 |

## 구현 원칙

- HTTP 상태/본문/result code 매핑은 `pyairkorea/_http.py`에 모읍니다.
- AirKorea raw field parsing은 `pyairkorea/client.py`의 모델 생성 함수와 `pyairkorea/_convert.py`에 둡니다.
- API 응답의 `body.items` shape는 사용자에게 노출하지 않습니다.
- 공백/`-`/`null` placeholder는 모델에서 `None`으로 변환합니다.
- 측정소 좌표 필드 `dmX`, `dmY`는 공식 필드명과 달리 사용자 모델에서는 `lat`, `lon`으로 의미를 드러냅니다.
- 좌표 변환은 `pyairkorea/coords.py`에서만 수행합니다.

## 테스트 매트릭스

기본 테스트는 네트워크 없이 실행됩니다.

| Area | Files | Coverage Intent |
|---|---|---|
| Type conversion | `tests/test_convert.py` | 날짜/시간/숫자/빈 값 처리 |
| Code mappings | `tests/test_codes.py` | 등급 라벨, 시도명, 예보코드, dataTerm 검증 |
| Coordinates | `tests/test_coords.py` | WGS84↔TM 변환, 좌표 범위 검증 |
| HTTP errors | `tests/test_http.py` | 인증/쿼터/no-data/5xx/네트워크/JSON 오류 |
| Client endpoints | `tests/test_client.py` | 모든 public method의 파라미터, 모델 타입, shape 정규화 |
| CLI | `tests/test_cli.py` | JSON 출력, env/explicit key, 위치 인자 검증 |

필수 검증 명령:

```bash
python -m compileall pyairkorea tests
python -m pytest
ruff check .
mypy pyairkorea
```

## Live API 테스트 정책

실제 AirKorea 호출은 기본 테스트에 넣지 않습니다.

- `AIRKOREA_SERVICE_KEY`가 있을 때만 동작하게 합니다.
- 테스트에는 `@pytest.mark.integration`을 붙입니다.
- 특정 측정값, 거리, 예보 문구를 고정값으로 단정하지 않습니다.
- 키와 호출 URL은 fixture에 저장하지 않습니다.

## 반복 실수 방지

이미 한 번 확인한 혼동 지점입니다.

- AirKorea JSON은 `items.item`만 있다고 가정하지 않습니다.
- `dmX`, `dmY`를 이름만 보고 x/y 평면좌표로 해석하지 않습니다.
- `getNearbyMsrstnList`에 위도/경도를 그대로 넣지 않습니다.
- 인증키 오류가 나면 Decoding/Encoding 키 혼동부터 확인합니다.
- `pm10Value`, `khaiValue` 같은 숫자 필드의 `-`는 0이 아니라 `None`입니다.
- 데이터는 실시간 미확정 자료일 수 있으므로 문서에 출처와 한계를 남깁니다.

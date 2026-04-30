# AirKorea OpenAPI 구현 명세

> 이 문서는 `pyairkorea` 구현자가 보는 레퍼런스입니다. 사용자용 빠른 설명은 [README.md](README.md)를 보세요.

## 1. 공식 출처

| 항목 | 값 |
|---|---|
| 제공기관 | 한국환경공단 |
| 포털 | 공공데이터포털 |
| 대기오염정보 데이터 | `한국환경공단_에어코리아_대기오염정보` |
| 측정소정보 데이터 | `한국환경공단_에어코리아_측정소정보` |
| 대기오염정보 Base URL | `http://apis.data.go.kr/B552584/ArpltnInforInqireSvc` |
| 측정소정보 Base URL | `http://apis.data.go.kr/B552584/MsrstnInfoInqireSvc` |
| 인증 파라미터 | `serviceKey` |
| 출력 형식 | `returnType=json` |
| 공식 포털 수정일 | 2026-03-03 |

공식 포털은 두 서비스 모두 JSON+XML을 제공한다고 안내합니다. 라이브러리 내부는 한글/타입 처리 안정성을 위해 JSON으로 고정합니다.

## 2. 공통 요청 규칙

| 파라미터 | 설명 |
|---|---|
| `serviceKey` | 공공데이터포털 인증키 |
| `returnType` | `json` 고정 |
| `numOfRows` | 목록형 API의 페이지 크기 |
| `pageNo` | 페이지 번호 |

주의:

- 라이브러리는 `requests`의 `params=`를 사용합니다.
- 인증키는 보통 Decoding 키를 넣는 편이 안전합니다.
- 일부 공공데이터 게이트웨이는 인증키 처리 방식이 흔들릴 수 있으므로, `SERVICE_KEY_IS_NOT_REGISTERED_ERROR`가 나면 Encoding/Decoding 키를 모두 확인합니다.
- API 오류가 JSON이 아니라 XML/평문으로 올 수 있어 HTTP 계층에서 텍스트 기반 인증/쿼터 오류도 매핑합니다.

## 3. 구현 범위

### 3.1 대기오염정보

| Method | Endpoint | 반환 |
|---|---|---|
| `station_measurements()` | `getMsrstnAcctoRltmMesureDnsty` | `list[AirQualityMeasurement]` |
| `latest_station_measurement()` | `getMsrstnAcctoRltmMesureDnsty` | `AirQualityMeasurement | None` |
| `sido_measurements()` | `getCtprvnRltmMesureDnsty` | `list[AirQualityMeasurement]` |
| `unhealthy_stations()` | `getUnityAirEnvrnIdexSnstiveAboveMsrstnList` | `list[AirQualityMeasurement]` |
| `forecast_notices()` | `getMinuDustFrcstDspth` | `list[ForecastNotice]` |
| `weekly_forecasts()` | `getMinuDustWeekFrcstDspth` | `list[WeeklyForecastNotice]` |

### 3.2 측정소정보

| Method | Endpoint | 반환 |
|---|---|---|
| `stations()` | `getMsrstnList` | `list[Station]` |
| `nearby_stations()` | `getNearbyMsrstnList` | `list[NearbyStation]` |
| `tm_coordinates()` | `getTMStdrCrdnt` | `list[TmCoordinate]` |
| `measurement_near()` | `getNearbyMsrstnList` + `getMsrstnAcctoRltmMesureDnsty` | `AirQualityMeasurement | None` |

## 4. 응답 shape

정상 JSON의 공통 뼈대:

```json
{
  "response": {
    "header": {
      "resultCode": "00",
      "resultMsg": "NORMAL_CODE"
    },
    "body": {
      "items": []
    }
  }
}
```

AirKorea는 API/시점에 따라 목록이 다음 두 형태로 올 수 있습니다.

```json
{"items": [{"stationName": "종로구"}]}
```

```json
{"items": {"item": {"stationName": "종로구"}}}
```

구현 규칙:

- `body.items`가 list이면 그대로 처리합니다.
- `body.items`가 dict이고 `item`을 가지면 `item`을 꺼냅니다.
- 단일 dict는 list 1개로 정규화합니다.
- 이상한 item shape는 `AirKoreaParseError`로 실패시킵니다.

## 5. 주요 필드 변환

### `AirQualityMeasurement`

| 원본 필드 | Python 필드 | 타입 |
|---|---|---|
| `stationName` | `station_name` | `str` |
| `dataTime` | `data_time` | `datetime | None`, KST aware |
| `mangName` | `mang_name` | `str | None` |
| `sidoName` | `sido_name` | `str | None` |
| `khaiValue` | `khai_value` | `int | None` |
| `khaiGrade` | `khai_grade` | `int | None` |
| `khaiGrade` | `khai_grade_label` | `str | None` |
| `so2Value`, `coValue`, `o3Value`, `no2Value` | `*_value` | `float | None` |
| `pm10Value`, `pm10Value24` | `pm10_value`, `pm10_value_24h` | `float | None` |
| `pm25Value`, `pm25Value24` | `pm25_value`, `pm25_value_24h` | `float | None` |
| `pm10Grade1h`, `pm25Grade1h` | `*_grade_1h` | `int | None` |

등급 라벨:

| 코드 | 라벨 |
|---|---|
| `1` | 좋음 |
| `2` | 보통 |
| `3` | 나쁨 |
| `4` | 매우나쁨 |

### `Station`

공식 응답의 `dmX`, `dmY`는 이름과 달리 WGS84 기반 좌표입니다.

| 원본 필드 | Python 필드 |
|---|---|
| `dmX` | `lat` |
| `dmY` | `lon` |

## 6. 좌표 정책

`getNearbyMsrstnList`는 TM 좌표를 받습니다.

- 직접 `tm_x`, `tm_y`를 알고 있으면 그대로 전달합니다.
- 위도/경도만 있으면 `wgs84_to_tm()`으로 변환합니다.
- 기본 변환 CRS는 과거 AirKorea 예시와 맞는 `EPSG:2097`입니다.
- 도로명주소 API X/Y 좌표를 쓰는 경우 AirKorea 문서의 `ver=1` 경로를 사용하므로, 변환하지 말고 `tm_x`, `tm_y`, `ver="1"`을 직접 넘깁니다.

## 7. Result Code 매핑

| 코드 | 의미 | 예외 |
|---|---|---|
| `00` | 정상 | 없음 |
| `03` | 데이터 없음 | `AirKoreaNoDataError` |
| `04` | HTTP 오류 | `AirKoreaServerError` |
| `12` | 서비스 없음/미신청 | `AirKoreaRequestError` |
| `20` | 접근 거부 | `AirKoreaAuthError` |
| `22` | 호출 제한 초과 | `AirKoreaRateLimitError` |
| `30` | 등록되지 않은 서비스키 | `AirKoreaAuthError` |
| `31` | 서비스키 만료 | `AirKoreaAuthError` |
| `99` | 기타 오류 | `AirKoreaServerError` |

## 8. 구현 체크리스트

- [x] `returnType=json` 고정
- [x] `serviceKey`는 request params로 전달
- [x] `items` list/dict/`items.item` 모두 정규화
- [x] `-`, 공백, `null`은 `None`으로 처리
- [x] `dmX`는 lat, `dmY`는 lon으로 노출
- [x] `khaiGrade` 라벨 제공
- [x] WGS84 -> TM 변환 지원
- [x] 네트워크 없는 단위 테스트 작성
- [x] 반복 실수 문서화

## 9. 공식 링크

- [한국환경공단_에어코리아_대기오염정보](https://www.data.go.kr/data/15073861/openapi.do)
- [한국환경공단_에어코리아_측정소정보](https://www.data.go.kr/en/data/15073877/openapi.do)

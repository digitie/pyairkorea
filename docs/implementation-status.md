# 구현 현황

2026-04-30 기준 AirKorea 계열 OpenAPI 11개 서비스군, 21개 endpoint 호출 경로를 구현했습니다.

## 상태표

| 서비스군 | Endpoint 수 | 상태 |
|---|---:|---|
| 대기오염정보 | 5 | 구현/테스트 완료 |
| 측정소정보 | 3 | 구현/테스트 완료 |
| 대기오염통계 현황 | 4 | 구현/테스트 완료 |
| 오존황사 발생정보 | 2 | 구현/테스트 완료 |
| 미세먼지 경보 발령 현황 | 1 | 구현/테스트 완료 |
| 사용자 지원 | 1 | 구현/테스트 완료 |
| 고농도 초미세먼지(50초과) 예보 정보 | 1 | 구현/테스트 완료 |
| 통합대기환경지수(CAI) 조회 서비스 | 1 | 구현/테스트 완료 |
| 국가배경농도 합성데이터 조회 서비스 | 1 | 구현/테스트 완료 |
| 측정소별 실시간 측정정보 영문 조회 서비스 | 1 | 구현/테스트 완료 |
| 측정소 영문 정보 조회 서비스 | 1 | 구현/테스트 완료 |

## 주요 코드 위치

| 영역 | 파일 |
|---|---|
| public client/API 목록 | `pyairkorea/client.py` |
| enum/코드 정규화 | `pyairkorea/codes.py` |
| 좌표 값 객체/좌표 변환 | `pyairkorea/coords.py` |
| HTTP envelope/result-code 처리 | `pyairkorea/_http.py` |
| Pydantic 응답 모델 | `pyairkorea/models.py` |
| 값 변환 | `pyairkorea/_convert.py` |

## 라이브러리 표면

- enum 입력: `DataTerm`, `InformCode`, `Pollutant`, `SidoName`, `StatsDataGubun`, `StatsSearchCondition`, `AirQualityGrade`
- 좌표 입력: WGS84는 `LatLon(lat, lon)`, AirKorea TM은 `TmPoint(tm_x, tm_y)`
- 기존 문자열 입력과 `lat=...`, `lon=...` 호출은 호환 유지
- 응답 모델은 Pydantic v2 `BaseModel` 기반이며 `raw`를 보존하면서 enum/좌표 property를 제공

## 테스트 매트릭스

| 테스트 | 검증 내용 |
|---|---|
| `tests/test_client.py` | 기존 대기오염정보/측정소정보/좌표 convenience 메서드 |
| `tests/test_expanded_api.py` | 누락 서비스군 endpoint, 파라미터, 모델 파싱 |
| `tests/test_http.py` | HTTP 상태, resultCode, JSON/XML 오류, `ServiceKey` 예외 |
| `tests/test_convert.py` | 날짜/시간/숫자/결측값 변환 |
| `tests/test_codes.py` | 등급, 시도명, 예보코드, dataTerm 검증 |
| `tests/test_coords.py` | WGS84/AirKorea TM 변환 |
| `tests/test_cli.py` | CLI JSON 출력과 인자 처리 |

## 필수 검증 명령

```bash
python -m compileall pyairkorea tests
python -m pytest
python -m pytest --cov=pyairkorea --cov-fail-under=90
python -m ruff check .
python -m mypy pyairkorea
```

## Live API 테스트 방침

실제 API 호출은 기본 테스트에서 제외합니다.

- 인증키와 포털 승인 상태가 필요합니다.
- 실시간 데이터는 측정소/시간/장비 상태에 따라 달라집니다.
- live 테스트를 추가할 때는 `@pytest.mark.integration`을 붙이고 `AIRKOREA_SERVICE_KEY`가 없으면 skip해야 합니다.
- live 테스트에서는 특정 농도값을 고정 assert하지 말고 envelope, 필드 존재, 타입 정도만 확인합니다.

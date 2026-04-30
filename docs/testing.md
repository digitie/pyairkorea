# 테스트 정책

`pyairkorea` 테스트는 기본적으로 **네트워크 없이** 돌아가야 합니다. AirKorea 실시간 데이터는 시점, 측정소 상태, 심의/운영계정 상태에 따라 쉽게 달라지므로 mock response 기반 테스트가 기본입니다.

## 원칙

- 기본 `pytest` 실행은 실 API를 호출하지 않습니다.
- 모든 endpoint 테스트는 fake session 또는 고정 fixture를 사용합니다.
- live 테스트는 `integration` marker로만 실행합니다.
- 타입 assertion을 반드시 포함합니다.
- 버그를 고칠 때는 먼저 실패하는 테스트를 추가합니다.

## 필수 오프라인 테스트

### 응답 정규화

- `body.items`가 list일 때
- `body.items`가 dict 하나일 때
- `body.items.item`이 dict 하나일 때
- `body.items.item`이 list일 때
- `body.items`가 비정상 타입일 때 `AirKoreaParseError`

### 타입 변환

- `dataTime="2026-04-30 14:00"`은 KST aware `datetime`
- `dataTime="2026-04-30 14시"`도 KST aware `datetime`
- `-`, 공백, `null`은 `None`
- `pm10Value`, `pm25Value`, `so2Value` 등은 `float | None`
- `khaiValue`, `khaiGrade` 등은 `int | None`
- 등급 1~4는 한국어 라벨로 매핑

### 좌표

- WGS84 위도/경도는 TM으로 변환 후 `tmX`, `tmY` 파라미터로 전달
- `tm_x/tm_y`와 `lat/lon`을 동시에 넘기면 실패
- 좌표 한쪽만 넘기면 실패
- 위도/경도 범위를 벗어나면 실패

### 오류 매핑

- HTTP 401/403 -> `AirKoreaAuthError`
- HTTP 429 -> `AirKoreaRateLimitError`
- HTTP 5xx -> retry 후 `AirKoreaServerError`
- `resultCode=03` -> `AirKoreaNoDataError`
- `resultCode=22` -> `AirKoreaRateLimitError`
- `resultCode=30/31` -> `AirKoreaAuthError`
- JSON 파싱 실패 + 서비스키 문자열 포함 -> `AirKoreaAuthError`

## Live 테스트

```bash
pytest -m integration
```

환경변수:

- `AIRKOREA_SERVICE_KEY`

규칙:

- 키가 없으면 skip
- 응답 shape와 타입만 검증
- 실제 측정값, 측정소 거리, 예보 문구는 고정하지 않음
- 호출량이 작은 endpoint부터 실행

## 회귀 테스트 우선순위

버그를 고칠 때는 항상:

1. 재현 fixture 또는 fake response 추가
2. 실패하는 테스트 작성
3. 구현 수정
4. README / 명세 / troubleshooting / repeated-mistakes 반영

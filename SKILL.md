# pyairkorea 작업 규칙

이 저장소를 이어서 작업할 때는 아래 순서를 지킵니다.

## API 목록 기준

- AirKorea 지원 범위는 `pyairkorea.client.SUPPORTED_ENDPOINTS`가 기준입니다.
- API 목록을 추가/수정하면 [airkorea-api.md](airkorea-api.md), [docs/implementation-status.md](docs/implementation-status.md), `tests/test_expanded_api.py`를 함께 수정합니다.
- 공공데이터포털 정적 HTML에 전체 상세기능이 보이지 않을 수 있으므로 공식 페이지, 검색 인덱스, 실제 게이트웨이 응답을 함께 대조합니다.

## 구현 원칙

- public method는 endpoint 하나에 명확히 매핑합니다.
- public method는 기존 문자열 입력과 새 enum 입력을 모두 받아야 합니다.
- 응답 Pydantic 모델은 확인된 주요 필드만 파싱하고 `raw`를 항상 보존합니다.
- 좌표 입력은 WGS84 `LatLon(lat, lon)` 또는 AirKorea TM `TmPoint(tm_x, tm_y)`를 우선 지원하고 기존 keyword 입력도 유지합니다.
- 값 변환은 `_convert.py`의 helper를 재사용합니다.
- 결측값은 `None`으로 보존하고 0으로 바꾸지 않습니다.
- endpoint 대소문자와 공식 오타처럼 보이는 철자를 임의로 고치지 않습니다.

## 테스트 원칙

- 새 public method는 fixture 기반 단위 테스트를 추가합니다.
- endpoint URL, 파라미터명, 날짜 변환, 모델 필드, 결측값 처리를 assert합니다.
- 실제 API 호출은 기본 테스트에 넣지 말고 integration marker로 분리합니다.

## 완료 전 확인

```bash
python -m compileall pyairkorea tests
python -m pytest
python -m pytest --cov=pyairkorea --cov-fail-under=90
python -m ruff check .
python -m mypy pyairkorea
```

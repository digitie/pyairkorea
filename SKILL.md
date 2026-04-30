# pyairkorea Agent Skill

이 저장소에서 작업하는 에이전트는 아래 규칙을 우선합니다.

## 기본 원칙

- AirKorea 공식 OpenAPI는 공공데이터포털의 `대기오염정보`와 `측정소정보` 두 서비스군으로 나눈다.
- 새 endpoint를 추가할 때는 먼저 [airkorea-api.md](airkorea-api.md)에 명세와 변환 정책을 기록한다.
- 사용자에게 raw AirKorea response shape를 직접 떠넘기지 않는다.
- 모든 public method는 네트워크 없는 테스트를 먼저 갖는다.
- bug fix는 실패 테스트, 구현, 문서 업데이트 순서로 진행한다.

## 구현 규칙

- HTTP/result-code 매핑은 `pyairkorea/_http.py`에서만 처리한다.
- raw 값 변환은 `pyairkorea/_convert.py`에 모은다.
- code/label/valid parameter는 `pyairkorea/codes.py`에 모은다.
- 좌표 변환은 `pyairkorea/coords.py`에서만 수행한다.
- 모델은 `dataclass(frozen=True, slots=True)`를 사용하고 raw record를 `raw`에 보존한다.
- `body.items`는 list, dict, `items.item` 모두 허용한다.
- 결측 placeholder인 `-`, 공백, `null`은 `None`으로 변환한다.
- `dmX`, `dmY`는 모델에서 `lat`, `lon`으로 바꿔 의미를 명확히 한다.

## 테스트 규칙

- 기본 `pytest`는 실 API 호출을 하지 않는다.
- fake session 또는 fixture로 HTTP를 고정한다.
- 실제 API 호출은 `integration` marker와 `AIRKOREA_SERVICE_KEY`가 있을 때만 허용한다.
- parser 변경 시 malformed response 테스트를 반드시 추가한다.
- 좌표 변경 시 `tests/test_coords.py`와 `docs/repeated-mistakes.md`를 함께 확인한다.

## 문서 규칙

- README는 사용자 관점의 빠른 사용법을 유지한다.
- `airkorea-api.md`는 구현자가 보는 정확한 명세/주의사항을 유지한다.
- 반복 실수는 발견 즉시 `docs/repeated-mistakes.md`에 추가한다.
- 오류 처리나 운영상의 함정은 `docs/troubleshooting.md`에 추가한다.

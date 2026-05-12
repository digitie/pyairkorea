# 테스트 원칙

`airkorea`의 기본 테스트는 네트워크 없이 항상 재현 가능해야 합니다.

## 기본 명령

```bash
python -m compileall src/airkorea tests
python -m pytest
python -m pytest --cov=airkorea --cov-fail-under=90
python -m ruff check .
python -m mypy src/airkorea
```

## 단위 테스트 기준

- 모든 public method는 endpoint URL과 주요 파라미터를 검증한다.
- 응답 parser는 list, 단일 dict, `items.item` 형태를 모두 처리해야 한다.
- 결측값 `-`, 빈 문자열, `null`은 `None`으로 변환한다.
- 숫자 문자열, 날짜 문자열, KST 시각 문자열을 타입으로 변환한다.
- 신규 API는 확인된 필드만 파싱하고 `raw` 보존을 전제로 한다.
- 서비스 목록은 `SUPPORTED_ENDPOINTS`와 `tests/test_expanded_api.py`가 서로 맞아야 한다.
- raw `call()`/`iter_pages()`는 인증키성 params를 실제 요청과 context에서 제거하고, `pageNo` 순회를 fixture로 검증한다.
- public API를 새로 추가하면 `tests/test_public_api.py`의 권장 export 목록도 함께 갱신한다.

## Live API 테스트 기준

실제 AirKorea 호출 테스트를 추가할 때는 다음 조건을 지킵니다.

- `@pytest.mark.integration`을 붙인다.
- `AIRKOREA_SERVICE_KEY`가 없으면 skip한다.
- 특정 농도값이나 문구를 고정 assert하지 않는다.
- 응답이 비어 있을 수 있는 API는 empty list를 실패로 보지 않는다.
- rate limit과 포털 장애를 고려해 CI 기본 경로에서는 실행하지 않는다.

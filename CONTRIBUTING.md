# Contributing

기여는 환영합니다. 이 프로젝트는 AirKorea OpenAPI 특성상 endpoint 철자와 응답 shape가 흔들릴 수 있으므로 테스트와 문서를 함께 갱신하는 방식을 권장합니다.

## 개발 환경

```bash
pip install -e ".[dev]"
```

## 변경 절차

1. 공식 공공데이터포털 문서 또는 실제 게이트웨이 응답으로 endpoint와 파라미터를 확인합니다.
2. `src/airkorea/client.py`에 public method와 parser를 추가합니다.
3. `src/airkorea/models.py`에 필요한 Pydantic 응답 모델을 추가합니다.
4. `tests/`에 fixture 기반 테스트를 추가합니다.
5. `airkorea-api.md`, `docs/implementation-status.md`, `docs/repeated-mistakes.md`를 갱신합니다.

## 문서 작성 규칙

- 저장소 문서는 한글로 작성합니다.
- 문서에서 파일 위치를 적을 때는 `src/airkorea/client.py`, `docs/testing.md`처럼 프로젝트 루트 기준 상대 경로만 사용합니다.
- Python 내부 문서(docstring과 유지보수용 설명 주석)도 한글로 작성합니다.
- endpoint, API 필드명, enum 값, 명령어, URL처럼 원문이 의미를 갖는 값은 그대로 둡니다.
- 자세한 기준은 `docs/documentation-style.md`를 확인하세요.

## 검증

```bash
python -m compileall src/airkorea tests
python -m pytest
python -m pytest --cov=airkorea --cov-fail-under=90
python -m ruff check .
python -m mypy src/airkorea
```

## Live API 테스트

실제 AirKorea 호출 테스트는 기본 테스트에 넣지 않습니다. 필요한 경우 `@pytest.mark.integration`을 사용하고 `AIRKOREA_SERVICE_KEY`가 없으면 skip하세요.

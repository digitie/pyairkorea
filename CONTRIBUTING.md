# Contributing

기여는 환영합니다. 이 프로젝트는 AirKorea OpenAPI 특성상 endpoint 철자와 응답 shape가 흔들릴 수 있으므로 테스트와 문서를 함께 갱신하는 방식을 권장합니다.

## 개발 환경

```bash
pip install -e ".[dev]"
```

## 변경 절차

1. 공식 공공데이터포털 문서 또는 실제 게이트웨이 응답으로 endpoint와 파라미터를 확인합니다.
2. `pyairkorea/client.py`에 public method와 parser를 추가합니다.
3. `pyairkorea/models.py`에 필요한 Pydantic 응답 모델을 추가합니다.
4. `tests/`에 fixture 기반 테스트를 추가합니다.
5. `airkorea-api.md`, `docs/implementation-status.md`, `docs/repeated-mistakes.md`를 갱신합니다.

## 검증

```bash
python -m compileall pyairkorea tests
python -m pytest
python -m pytest --cov=pyairkorea --cov-fail-under=90
python -m ruff check .
python -m mypy pyairkorea
```

## Live API 테스트

실제 AirKorea 호출 테스트는 기본 테스트에 넣지 않습니다. 필요한 경우 `@pytest.mark.integration`을 사용하고 `AIRKOREA_SERVICE_KEY`가 없으면 skip하세요.

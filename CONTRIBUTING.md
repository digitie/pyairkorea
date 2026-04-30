# Contributing

`pyairkorea`는 API shape가 바뀌어도 사용자가 덜 흔들리도록 하는 작은 라이브러리입니다. 기여할 때는 구현보다 회귀 방지를 조금 더 중요하게 봅니다.

## 개발 환경

```bash
python -m venv .venv
pip install -e ".[dev]"
```

## 변경 전 체크

- 새 endpoint라면 `airkorea-api.md`에 먼저 범위와 응답 필드를 정리합니다.
- 기존 버그라면 재현 테스트를 먼저 추가합니다.
- 실제 API 응답을 저장할 때는 인증키와 개인 위치 정보를 제거합니다.

## 제출 전 검증

```bash
python -m compileall pyairkorea tests
python -m pytest
ruff check .
mypy pyairkorea
```

## 문서 업데이트

- 사용법이 바뀌면 `README.md`
- API 규칙이 바뀌면 `airkorea-api.md`
- 테스트 정책이 바뀌면 `docs/testing.md`
- 같은 실수를 막고 싶으면 `docs/repeated-mistakes.md`
- 사용자 오류 대응이 늘면 `docs/troubleshooting.md`

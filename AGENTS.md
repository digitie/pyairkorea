# pyairkorea 작업 운영 규칙

## 목표

`pyairkorea`는 한국환경공단 AirKorea OpenAPI를 Python에서 안전하게 쓰기 위한 얇고 타입 안전한 클라이언트입니다. 실시간 대기질 데이터의 특성과 공공데이터포털 게이트웨이의 흔들림을 라이브러리 내부에서 최대한 흡수합니다.

## 작업 순서

1. 공식 명세나 실제 응답 shape를 확인한다.
2. 문서에 범위와 변환 정책을 먼저 적는다.
3. 실패하는 테스트를 작성한다.
4. 구현한다.
5. `compileall`, `pytest`, `ruff`, `mypy`를 실행한다.
6. 반복 실수 또는 troubleshooting 문서를 갱신한다.

## 금지 사항

- 기본 테스트에서 실 API를 호출하지 않는다.
- 인증키가 포함된 URL, fixture, 로그를 커밋하지 않는다.
- `items.item`만 지원하는 parser로 되돌리지 않는다.
- 결측 값을 0으로 바꾸지 않는다.
- `dmX/dmY`를 평면좌표처럼 노출하지 않는다.
- 사용자가 넘긴 좌표를 조용히 다른 좌표계라고 가정하지 않는다.

## 검증 명령

```bash
python -m compileall pyairkorea tests
python -m pytest
ruff check .
mypy pyairkorea
```

## 참고 프로젝트에서 가져온 패턴

- `pykma`: 공공데이터포털 인증키 처리, result code 매핑, 시간/코드 helper 분리
- `pyopinet`: 명세 문서와 implementation status, 타입 변환 책임을 라이브러리에 둠
- `pykrairport`: provider/API shape 차이를 adapter 내부에서 흡수, fixture 기반 테스트 우선

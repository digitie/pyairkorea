# AGENTS

`pyairkorea`는 한국환경공단 AirKorea OpenAPI용 Python 클라이언트입니다. 작업할 때는 기존 사용자 변경을 되돌리지 말고, 작은 단위로 검증하면서 진행합니다.

## 저장소 구조

- `pyairkorea/client.py`: public client, base URL, endpoint 목록
- `pyairkorea/models.py`: public dataclass 모델
- `pyairkorea/_http.py`: HTTP 호출, retry, resultCode 예외 매핑
- `pyairkorea/_convert.py`: 문자열/숫자/날짜 변환 helper
- `tests/`: 네트워크 없는 fixture 기반 단위 테스트
- `docs/`: 구현 상태, 테스트 정책, 반복 실수 방지, 문제 해결 문서

## 작업 규칙

- API 목록은 `SUPPORTED_ENDPOINTS`와 [airkorea-api.md](airkorea-api.md)를 기준으로 한다.
- 새 API를 추가하면 코드, 테스트, 문서를 함께 수정한다.
- 신규 응답 스키마가 불확실하면 확인된 필드만 파싱하고 `raw`를 보존한다.
- destructive git 명령은 사용하지 않는다.
- 커밋 전 `pytest`, `ruff`, `mypy`, coverage를 통과시킨다.

## 특히 조심할 점

- `getCtprvnMesureLIst`, `getCtprvnMesureSidoLIst`의 `LIst` 철자를 바꾸지 않는다.
- 월평균 endpoint는 `getMsrstnAcctoRMmrg`다.
- 사용자 지원 API는 `ServiceKey` 대문자 파라미터를 쓴다.
- 영문 API는 `atmstMsrstnRltmInfo/getList`, `atmstMsrstnInfoEngNm/getList`다.

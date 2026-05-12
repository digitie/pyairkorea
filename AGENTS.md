# AGENTS.md

## 역할

이 문서는 Codex/agent가 `python-airkorea-api`에서 작업하기 전에 읽는 운영 가이드입니다. 빠르게 방향을 잡기 위한 문서이며, API 세부 명세는 `airkorea-api.md`, 구현 세부 규칙은 `SKILL.md`와 `docs/` 아래 문서를 함께 확인합니다.

## 지시 우선순위

1. 사용자 요청
2. 이 `AGENTS.md`
3. `airkorea-api.md`
4. `SKILL.md`
5. `README.md`와 `docs/` 문서
6. 기존 코드와 테스트
7. 최소한의, 되돌릴 수 있는 가정

문서가 충돌하면 더 높은 우선순위의 문서를 따르고, 필요하면 낮은 우선순위 문서를 함께 갱신합니다.

## 프로젝트 기준

- `python-airkorea-api`는 한국환경공단 AirKorea OpenAPI용 비공식 Python 클라이언트입니다.
- Python import 이름은 `airkorea`입니다.
- 지원 범위는 공공데이터포털의 AirKorea 계열 B552584 OpenAPI이며, 비점오염원/재활용/냉매 같은 비-AirKorea 서비스는 범위 밖입니다.
- 구현 기준 목록은 `src/airkorea/client.py`의 `SUPPORTED_ENDPOINTS`와 `airkorea-api.md`입니다.
- Python 지원 기준은 3.10 이상입니다.
- 런타임 의존성은 `pydantic`, `kraddr.base`, `pyproj`, `requests`입니다.
- 기본 테스트는 실제 AirKorea 네트워크 호출 없이 fixture/fake session으로 동작해야 합니다.

## 핵심 불변 조건

- 실제 `AIRKOREA_SERVICE_KEY`나 원본 인증키를 코드, fixture, 로그, 문서, 커밋에 남기지 않습니다.
- 대부분의 API 인증 파라미터는 `serviceKey`이지만 `UserSportSvc/getSvckeyDalyStats`는 공식 명세대로 `ServiceKey`를 사용합니다.
- `getCtprvnMesureLIst`, `getCtprvnMesureSidoLIst`의 `LIst` 철자를 바꾸지 않습니다.
- 월평균 endpoint는 `getMsrstnAcctoRMmrg`입니다. `getMsrstnAcctoRmmrg`로 고치지 않습니다.
- 영문 API는 `atmstMsrstnRltmInfo/getList`, `atmstMsrstnInfoEngNm/getList`입니다.
- HTTP 200이어도 body의 `resultCode` 실패는 typed exception으로 처리합니다.
- `body.items`, 단일 dict, `items.item` 응답 shape를 모두 정규화합니다.
- 신규 응답 스키마가 불확실하면 확인된 필드만 Pydantic 모델로 파싱하고 `raw`를 보존합니다.
- 결측값 `-`, 빈 문자열, `null`, `none`, `nan`은 `None`으로 처리하고 0으로 바꾸지 않습니다.
- enum/type을 추가할 때 기존 문자열 입력 호환성을 유지합니다.
- WGS84 public 좌표는 `kraddr.base.PlaceCoordinate(lon, lat)` 순서, AirKorea TM 좌표는 `TmPoint(tm_x, tm_y)` 순서로 고정합니다.
- 기존 `LatLon(lat, lon)`, tuple, mapping, `lat=...`, `lon=...` 입력 호환성은 유지합니다.
- 측정소정보의 `dmX`, `dmY`는 샘플 기준 위도/경도이며, 근접 측정소 API는 별도 TM 좌표를 요구합니다.

## 문서 라우팅

- 사용자용 개요와 예시: `README.md`
- 공식 API 목록, endpoint, Python 메서드 매핑: `airkorea-api.md`
- 라이브러리 표면, enum, 좌표, raw page 사용법: `docs/library-surface.md`
- 구현 상태와 테스트 매트릭스: `docs/implementation-status.md`
- 문서와 Python 내부 문서 작성 규칙: `docs/documentation-style.md`
- 테스트 원칙과 live test 방침: `docs/testing.md`
- 반복 실수 방지 로그: `docs/repeated-mistakes.md`
- 오류별 점검표: `docs/troubleshooting.md`
- 구현 불변조건과 완료 전 확인: `SKILL.md`
- 기여 절차: `CONTRIBUTING.md`
- 패키징, 의존성, lint/test 설정: `pyproject.toml`

## 모듈 지도

- `src/airkorea/client.py`: public client, base URL, endpoint 목록, typed convenience method
- `src/airkorea/models.py`: public Pydantic 응답 모델과 raw page 모델
- `src/airkorea/_http.py`: HTTP 호출, retry, resultCode 예외 매핑
- `src/airkorea/_convert.py`: 문자열/숫자/날짜/결측값 변환 helper
- `src/airkorea/codes.py`: enum, 코드 라벨, 입력 검증 helper
- `src/airkorea/coords.py`: WGS84 호환 입력과 AirKorea TM 값 객체/좌표 변환
- `src/airkorea/metadata.py`: 인증키 제거, 호출 context, cache key
- `src/airkorea/pagination.py`: pageNo/numOfRows/totalCount 기반 페이지 순회 helper
- `src/airkorea/cli.py`: CLI entrypoint
- `tests/`: 네트워크 없는 fixture/fake session 기반 단위 테스트

## 문서 작성 규칙

- 저장소에 남기는 문서는 한글로 작성합니다.
- 문서에서 파일 위치를 언급할 때는 프로젝트 루트 기준 상대 경로만 씁니다. 예: `src/airkorea/client.py`, `docs/implementation-status.md`.
- 로컬 시스템의 드라이브나 홈 디렉터리에서 시작하는 절대 경로는 실행 로그나 임시 대화에만 쓰고 저장소 문서에는 남기지 않습니다.
- Python 내부 문서, 즉 모듈/클래스/함수/메서드 docstring과 유지보수용 설명 주석은 한글로 작성합니다.
- API 필드명, endpoint, enum 값, 명령어, URL, 외부 오류 메시지처럼 원문 자체가 의미 있는 값은 그대로 둡니다.

## 작업 원칙

- API를 추가하거나 수정하면 코드, fixture 기반 테스트, `airkorea-api.md`, 관련 `docs/` 문서를 같은 변경 단위에서 갱신합니다.
- 구현 전에는 `SUPPORTED_ENDPOINTS`, `airkorea-api.md`, `SKILL.md`의 관련 규칙을 확인합니다.
- public method는 endpoint 하나에 명확히 매핑하고, 요청 파라미터 검증은 HTTP 호출 전에 수행합니다.
- 값 변환은 `src/airkorea/_convert.py` helper를 재사용합니다.
- 응답 모델은 외부 프로그램에서 쓰기 쉽게 Python 타입과 enum property를 제공하되 원본 `raw`를 보존합니다.
- 불필요한 wrapper, adapter, compatibility layer를 만들어 차이를 숨기기보다 기존 public surface와 내부 구현에 필요한 동작을 직접 반영합니다.
- 다른 라이브러리에서 검증된 구현 방식이나 동작 규칙이 확인되면 최소수정 원칙과 다소 어긋나더라도 임시 우회 wrapper를 추가하지 말고 해당 내용을 라이선스 허용 범위 안에서 바로 적용합니다.
- 실제 API 호출이 필요한 테스트는 `@pytest.mark.integration`으로 분리하고 기본 테스트 경로에서는 실행하지 않습니다.
- 변경은 작은 완성 단위로 만들고, 기존 사용자 변경을 되돌리지 않습니다.
- destructive git 명령은 사용하지 않습니다.

## 로컬 환경 주의

- 이 Windows 작업 환경에서는 `rg`가 실행 권한 문제로 실패할 수 있습니다. `rg`가 `Access is denied`를 내면 반복 시도하지 말고 `git ls-files`, `Get-ChildItem`, `Select-String`으로 우회합니다.
- 한글 문서를 PowerShell에서 읽을 때는 UTF-8을 명시합니다. 예: `[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new(); Get-Content -Encoding UTF8 -Raw AGENTS.md`
- 문서가 깨져 보이면 먼저 인코딩 문제를 의심하고, 파일 내용을 잘못된 문자로 덮어쓰지 않습니다.

## 검증 기준

기본 검증:

```bash
python -m compileall src/airkorea tests
python -m pytest
```

커밋/푸시 전 검증:

```bash
python -m pytest --cov=airkorea --cov-fail-under=90
python -m ruff check .
python -m mypy src/airkorea
```

실제 API 테스트를 추가할 경우 opt-in으로 둡니다.

```bash
AIRKOREA_SERVICE_KEY=<decoded service key> python -m pytest -m integration
```

## 반복 실수 방지

- AirKorea API를 대기오염정보/측정소정보 2개 서비스군으로만 단정하지 않습니다.
- endpoint 대소문자와 오타처럼 보이는 공식 철자를 임의로 고치지 않습니다.
- `serviceKey`와 `ServiceKey` 예외를 섞지 않습니다.
- 영문 서비스 URL을 기존 한글 서비스명에 `EngSvc`를 붙이는 방식으로 추측하지 않습니다.
- `dmX`, `dmY`와 근접 측정소용 TM 좌표를 섞지 않습니다.
- 실시간 데이터 값이나 예보 문구를 고정값 테스트로 만들지 않습니다.

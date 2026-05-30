# CLAUDE.md — 프로젝트 컨텍스트

이 파일은 Claude Code 및 여러 에이전트들이 매 세션 시작 시 자동으로 로드하여 프로젝트의 현재 상태와 연속성을 파악하는 진입점이다.
프로젝트에 관한 상세 규칙은 `AGENTS.md`에, 구현 규칙은 `SKILL.md`에, 아키텍처 ADR은 `docs/decisions.md`에 정의되어 있다.

## 프로젝트 현황 (2026-05-31)

한국환경공단 AirKorea OpenAPI용 비공식 Python 비동기/동기 하이브리드 클라이언트.
현재 `main` 브랜치는 httpx 기반의 비동기 파사드 클라이언트(`AirKoreaClient`)와 pydantic을 이용한 안정된 public client, typed model, enum, 좌표 변환(`coords.py`)이 구현되어 있다.
모든 문서는 한글로 작성되며(예외 없음 — `AGENTS.md` 언어 정책), `docs/` 내에서 일지, 결정사항, 백로그를 체계적으로 추적한다.

### 현재 작업

- maplibre-vworld-js 스타일 이식 및 MCP 설정 구성 (`chore/adopt-vworld-agent-style` 브랜치)

### 잔존 기술 부채

- (없음 — 새 부채가 발견되면 `docs/tasks.md`에 T-NNN으로 등록한다)

### 브랜치 정리

- `codex/remove-kraddr-base-clean` — 리모트 정리 대상
- `codex/wsl-kraddr-debug-ui-docs` — 리모트 정리 대상

### 후속 백로그

- T-001: AirKorea CLI 기능 고도화 (JSON 포맷팅 및 파라미터 매핑 개선)
- T-002: `@pytest.mark.integration` 통합 테스트 커버리지 확대
- T-003: 캐싱 데코레이터 또는 메모리 캐시 미들웨어 추가 검토

---

## 에이전트 worktree + CodeGraph

ChatGPT Codex는 `F:\dev\python-airkorea-api-codex`, Claude Code는 `F:\dev\python-airkorea-api-claude`, Google Antigravity는 `F:\dev\python-airkorea-api-antigravity`를 고정 worktree로 사용한다. 새 작업은 해당 worktree에서 `git fetch` 후 `git switch -c agent/<topic> main`으로 브랜치를 딴다.
CodeGraph는 각 에이전트 worktree에서 `codegraph init -i`로 1회 초기화한 뒤 `codegraph sync`로 인덱스를 동기화한다.

---

## 로컬 개발 환경

```
F:\dev\python-airkorea-api\
├── src/airkorea/         # Python 패키지 소스
│   ├── client.py         # public client, base URL, 편리 메서드
│   ├── models.py         # public Pydantic 응답 모델
│   ├── _http.py          # HTTP 호출, retry, resultCode 예외 매핑
│   ├── _convert.py       # 문자열/숫자/결측값 변환 helper
│   ├── codes.py          # enum, 코드 라벨, 입력 검증
│   ├── coords.py         # WGS84 좌표 ⇄ AirKorea TM 좌표 변환
│   ├── metadata.py       # 호출 context 및 cache key
│   ├── pagination.py     # pageNo/numOfRows 기반 페이지 순회 helper
│   └── cli.py            # CLI 진입점
├── tests/                # 네트워크 없는 fixture/fake session 기반 단위 테스트
└── docs/                 # decisions, journal, tasks, resume 등 에이전트 문서
```

* Python 3.10 이상 지원.
* 주요 의존성: `pydantic`, `pyproj`, `httpx`.

---

## 빠른 검증 명령

```bash
# 코드 정적 검증
python -m compileall src/airkorea tests

# 단위 테스트 실행 (네트워크 없음)
python -m pytest

# 테스트 커버리지 검증 (90% 이상 강제)
python -m pytest --cov=airkorea --cov-fail-under=90

# 린트 및 포맷 코드스타일 검사
python -m ruff check .

# 정적 타입 검사
python -m mypy src/airkorea

# 실제 API 연동 테스트 실행 (Decoded 서비스키 필요, Opt-in)
DATA_GO_KR_SERVICE_KEY=<decoded_service_key> python -m pytest -m integration
```

---

## 작업 후 의무사항

1. `docs/journal.md`에 변경 사항 항목 추가 (날짜·요약·결정·다음 작업, 역시간순)
2. `docs/tasks.md`에서 현재 작업 상태 업데이트 (T-NNN 상태 갱신)
3. 새로운 아키텍처 결정이 있었다면 `docs/decisions.md`에 ADR 추가
4. 사용자 가시 변경이 존재하면 `CHANGELOG.md` 갱신
5. PR 머지 전 로컬에서 빠른 검증 명령 5종 세트(`compileall`, `pytest`, `cov`, `ruff`, `mypy`)가 100% 성공함을 검증할 것.

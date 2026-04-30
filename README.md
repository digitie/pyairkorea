# pyairkorea

한국환경공단 AirKorea OpenAPI를 Python에서 편하게 쓰기 위한 비공식 클라이언트 라이브러리입니다.

`pyairkorea`는 공공데이터포털의 `한국환경공단_에어코리아_대기오염정보`와 `한국환경공단_에어코리아_측정소정보` API를 감싸고, 실시간 측정값/측정소/근접 측정소/예보 통보 데이터를 Python dataclass와 네이티브 타입으로 제공합니다.

> 공식 포털 기준 수정일은 2026-03-03입니다. 세부 명세와 구현 주의사항은 [airkorea-api.md](airkorea-api.md), 반복 실수 방지는 [docs/repeated-mistakes.md](docs/repeated-mistakes.md)를 참고하세요.

---

## 핵심 특징

- **대기오염정보 + 측정소정보 통합**: 측정소별 실시간 측정정보, 시도별 측정정보, 나쁨 이상 측정소, 예보통보, 주간예보, 측정소 목록, 근접 측정소, TM 기준좌표를 한 클라이언트에서 호출합니다.
- **JSON shape 흔들림 흡수**: AirKorea 응답의 `body.items`가 list로 오거나 `items.item`으로 오거나 모두 처리합니다.
- **Python 타입 변환**: 숫자 문자열, 등급 코드, 날짜/시간 문자열, 빈 값(`-`, 공백, `null`)을 모델 경계에서 안전하게 변환합니다.
- **등급 라벨 제공**: `khaiGrade=1..4`를 `좋음`, `보통`, `나쁨`, `매우나쁨` 라벨로 함께 제공합니다.
- **WGS84 -> AirKorea TM 변환**: 위도/경도로 가까운 측정소를 찾을 수 있도록 EPSG:2097 기반 변환 헬퍼를 제공합니다.
- **명확한 예외 계층**: 인증, no-data, 호출제한, 네트워크, 서버, 파싱 오류를 구분합니다.
- **네트워크 없는 기본 테스트**: API fixture/mock 기반 테스트를 기본으로 두고, 실제 호출은 별도 integration marker로 분리합니다.

---

## 시작하기

### 1단계: 인증키 발급

1. [공공데이터포털](https://www.data.go.kr)에 가입하고 로그인합니다.
2. `한국환경공단_에어코리아_대기오염정보`와 `한국환경공단_에어코리아_측정소정보`에 활용신청합니다.
3. 발급받은 서비스키를 환경변수로 저장합니다.

```bash
export AIRKOREA_SERVICE_KEY="발급받은_디코딩_인증키"
```

Windows PowerShell:

```powershell
$env:AIRKOREA_SERVICE_KEY="발급받은_디코딩_인증키"
```

`pyairkorea`는 `requests.get(..., params=...)`로 호출하므로 보통 **Decoding 인증키** 사용을 권장합니다. 포털 또는 게이트웨이 상태에 따라 Encoding 키가 동작하는 경우도 있으니, 인증 오류가 나면 두 키를 모두 점검하세요.

### 2단계: 설치

개발 중인 로컬 저장소 기준:

```bash
pip install -e ".[dev]"
```

### 3단계: 사용

```python
from pyairkorea import AirKoreaClient

air = AirKoreaClient.from_env()

latest = air.latest_station_measurement("종로구")
if latest:
    print(latest.data_time, latest.pm10_value, latest.pm25_value, latest.khai_grade_label)

for row in air.sido_measurements("서울", num_of_rows=5):
    print(row.station_name, row.pm10_value, row.pm25_value)
```

위도/경도로 가까운 측정소를 찾고 최신 측정값을 가져올 수도 있습니다.

```python
nearby = air.nearby_stations(lat=37.5665, lon=126.9780)
print(nearby[0].station_name, nearby[0].distance_km)

measurement = air.measurement_near(lat=37.5665, lon=126.9780)
```

측정소 목록과 예보통보:

```python
stations = air.stations(addr="서울", station_name="종로구")
notices = air.forecast_notices(search_date="2026-04-30", inform_code="PM10")
weekly = air.weekly_forecasts(search_date="2026-04-30")
```

---

## CLI

```bash
pyairkorea station --station-name 종로구
pyairkorea sido --sido-name 서울 --num-of-rows 25
pyairkorea stations --addr 서울
pyairkorea nearby --lat 37.5665 --lon 126.9780
pyairkorea forecast --search-date 2026-04-30 --inform-code PM10
```

출력은 UTF-8 JSON입니다.

---

## 개발

```bash
python -m compileall pyairkorea tests
python -m pytest
ruff check .
mypy pyairkorea
```

실제 API 호출 테스트는 기본 테스트에 넣지 않습니다. 필요한 경우 `AIRKOREA_SERVICE_KEY`가 있을 때만 `pytest -m integration` 형태로 분리합니다.

---

## 문서

- [airkorea-api.md](airkorea-api.md): 구현용 API 명세와 범위
- [docs/implementation-status.md](docs/implementation-status.md): 구현 상태와 테스트 매트릭스
- [docs/testing.md](docs/testing.md): 테스트 정책
- [docs/repeated-mistakes.md](docs/repeated-mistakes.md): 반복 실수 방지 로그
- [docs/troubleshooting.md](docs/troubleshooting.md): 오류별 점검법
- [SKILL.md](SKILL.md): 이후 에이전트가 따라야 할 구현 규칙
- [AGENTS.md](AGENTS.md): 작업 운영 규칙

## 참고

- [한국환경공단_에어코리아_대기오염정보](https://www.data.go.kr/data/15073861/openapi.do)
- [한국환경공단_에어코리아_측정소정보](https://www.data.go.kr/en/data/15073877/openapi.do)

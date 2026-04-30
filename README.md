# pyairkorea

한국환경공단 AirKorea OpenAPI를 Python에서 쓰기 쉽게 감싼 비공식 클라이언트입니다.

`pyairkorea`는 공공데이터포털의 AirKorea 계열 B552584 OpenAPI를 dataclass 기반의 안정적인 Python 객체로 변환합니다. 2026-04-30 기준으로 확인한 AirKorea 대기오염정보, 측정소정보, 통계, 오존/황사, 미세먼지 경보, 사용자 지원, 고농도 PM2.5 예보, CAI, 국가배경농도 합성데이터, 영문 측정정보/측정소정보 서비스를 구현했습니다.

## 설치

```bash
pip install pyairkorea
```

개발 환경:

```bash
pip install -e ".[dev]"
```

## 인증키

공공데이터포털에서 필요한 AirKorea OpenAPI 활용신청을 한 뒤 일반 인증키를 환경변수로 저장합니다.

```bash
export AIRKOREA_SERVICE_KEY="발급받은_인증키"
```

PowerShell:

```powershell
$env:AIRKOREA_SERVICE_KEY="발급받은_인증키"
```

`requests.get(..., params=...)`로 호출하므로 보통 Decoding 인증키 사용을 권장합니다. 인증 오류가 나면 Encoding/Decoding 키를 모두 확인하세요.

## 빠른 사용

```python
from pyairkorea import AirKoreaClient

air = AirKoreaClient.from_env()

latest = air.latest_station_measurement("종로구")
if latest:
    print(latest.data_time, latest.pm10_value, latest.pm25_value, latest.khai_grade_label)

for row in air.sido_measurements("서울", num_of_rows=5):
    print(row.station_name, row.pm10_value, row.pm25_value)
```

좌표로 가까운 측정소를 찾고 최신 측정값을 가져올 수도 있습니다.

```python
measurement = air.measurement_near(lat=37.5665, lon=126.9780)
```

## 지원 API

| 서비스 | 주요 메서드 |
|---|---|
| 대기오염정보 | `station_measurements`, `sido_measurements`, `unhealthy_stations`, `forecast_notices`, `weekly_forecasts` |
| 측정소정보 | `stations`, `nearby_stations`, `tm_coordinates`, `measurement_near` |
| 대기오염통계 현황 | `sido_average_stats`, `city_average_stats`, `station_daily_stats`, `station_monthly_stats` |
| 오존황사 발생정보 | `ozone_advisories`, `yellow_dust_advisories` |
| 미세먼지 경보 발령 현황 | `dust_alarms` |
| 사용자 지원 | `traffic_stats` |
| 고농도 초미세먼지(50초과) 예보 정보 | `high_pm25_forecasts` |
| 통합대기환경지수(CAI) 조회 | `cai_measurements` |
| 대기오염물질 국가배경농도 합성데이터 | `background_concentrations` |
| 측정소별 실시간 측정정보 영문 조회 | `english_measurements` |
| 측정소 영문 정보 조회 | `english_stations` |

전체 endpoint 목록과 정확한 철자는 [airkorea-api.md](airkorea-api.md)를 확인하세요.

## 예시

```python
from datetime import date

stats = air.sido_average_stats(item_code="PM10", data_gubun="HOUR")
alarms = air.dust_alarms(2026, item_code="PM25")
ozone = air.ozone_advisories(year=2026)
traffic = air.traffic_stats(date(2026, 4, 30))
english = air.english_stations(station_name="Sangdae")
```

## CLI

CLI는 자주 쓰는 조회를 중심으로 제공합니다. 전체 API는 Python 클라이언트에서 사용할 수 있습니다.

```bash
pyairkorea station --station-name 종로구
pyairkorea sido --sido-name 서울 --num-of-rows 25
pyairkorea stations --addr 서울
pyairkorea nearby --lat 37.5665 --lon 126.9780
pyairkorea forecast --search-date 2026-04-30 --inform-code PM10
```

## 개발 검증

```bash
python -m compileall pyairkorea tests
python -m pytest
python -m pytest --cov=pyairkorea --cov-fail-under=90
python -m ruff check .
python -m mypy pyairkorea
```

실제 API 호출 테스트는 기본 테스트에 넣지 않습니다. 네트워크, 인증키, 실시간 데이터 상태가 흔들리기 때문입니다.

## 문서

- [airkorea-api.md](airkorea-api.md): 공식 API 목록, endpoint, 메서드 매핑
- [docs/implementation-status.md](docs/implementation-status.md): 구현/테스트 현황
- [docs/testing.md](docs/testing.md): 테스트 원칙
- [docs/repeated-mistakes.md](docs/repeated-mistakes.md): 반복 실수 방지 로그
- [docs/troubleshooting.md](docs/troubleshooting.md): 오류별 점검표
- [SKILL.md](SKILL.md): 이후 에이전트가 따라야 할 구현 규칙
- [AGENTS.md](AGENTS.md): 협업/작업 규칙

## 범위

이 패키지는 AirKorea 대기질 API 클라이언트입니다. 한국환경공단의 모든 B552584 서비스(비점오염원, 재활용, 냉매 등)를 포함하지 않습니다.

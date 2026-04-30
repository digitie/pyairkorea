# Troubleshooting

## `AirKoreaAuthError: SERVICE_KEY...`

가능한 원인:

- 공공데이터포털 활용신청이 아직 승인되지 않음
- 대기오염정보와 측정소정보 중 하나만 신청함
- Encoding 키를 `params=`로 넘겨 다시 인코딩됨
- Decoding 키가 필요한 게이트웨이에 Encoding 키를 사용함

점검:

```python
from pyairkorea import AirKoreaClient

air = AirKoreaClient("디코딩키")
air.stations(addr="서울", num_of_rows=1)
```

Decoding 키가 실패하면 Encoding 키도 한 번 확인합니다. 공공데이터포털 게이트웨이 쪽 키 처리 방식이 시점에 따라 달라질 수 있습니다.

## `AirKoreaNoDataError`

가능한 원인:

- 측정소명이 정확하지 않음
- `dataTerm` 범위 안에 데이터가 없음
- 예보통보 `searchDate` 또는 `InformCode` 조건이 너무 좁음
- API 신청 또는 운영계정 권한이 endpoint와 맞지 않음

점검:

- `air.stations(station_name="종로구")`로 실제 측정소명을 먼저 확인
- `num_of_rows`를 늘려 확인
- `forecast_notices()`를 조건 없이 호출해 최근 목록 shape만 확인

## 가까운 측정소가 이상함

가능한 원인:

- `tmX`, `tmY`에 위도/경도를 그대로 넣음
- 도로명주소 API 좌표를 변환해서 이중 변환함
- AirKorea legacy TM과 도로명주소 API 좌표 버전을 혼동함

점검:

```python
air.nearby_stations(lat=37.5665, lon=126.9780)
```

도로명주소 API 좌표를 이미 가지고 있다면:

```python
air.nearby_stations(tm_x=945959.1814, tm_y=1953851.96028, ver="1")
```

## `AirKoreaParseError`

가능한 원인:

- JSON이 아닌 XML/HTML이 반환됨
- API 응답 shape가 변경됨
- 숫자 필드에 예상하지 못한 문자열이 들어옴

점검:

- 같은 호출을 `returnType=json`으로 직접 확인
- raw response를 저장할 때 인증키를 반드시 제거
- 재현 fixture를 추가하고 parser 테스트부터 작성

## PowerShell에서 한글이 깨져 보임

가능한 원인:

- 콘솔 출력 인코딩이 CP949라 UTF-8 JSON이 mojibake로 표시됨

점검:

```powershell
$env:PYTHONIOENCODING="utf-8"
pyairkorea station --station-name 종로구
```

파일 자체는 UTF-8로 유지하고, 테스트에서는 실제 한국어 문자열을 비교합니다.

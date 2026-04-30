# 반복 실수 방지 로그

이 문서는 `pyairkorea`를 만들면서 반복하기 쉬운 실수를 기록합니다. 같은 문제가 코드 리뷰나 디버깅에서 한 번 더 보이면 테스트를 추가하고 이 문서를 갱신합니다.

## 1. `items.item`만 있다고 가정하는 실수

- 증상: `KeyError: 'item'` 또는 빈 결과
- 원인: AirKorea JSON은 KMA와 달리 `body.items`가 list로 바로 오는 경우가 흔함
- 규칙: `body.items`, `body.items.item`, 단일 dict를 모두 정규화
- 가드레일: `tests/test_client.py`에서 세 shape 모두 고정

## 2. `dmX`, `dmY`를 평면좌표 X/Y로 오해하는 실수

- 증상: 측정소 메타데이터 좌표가 엉뚱하게 표시됨
- 원인: 공식 응답 설명은 `dmX`를 WGS84 기반 X 좌표라고 쓰지만 실제 샘플은 위도, `dmY`는 경도
- 규칙: 모델에서는 `Station.lat = dmX`, `Station.lon = dmY`로 노출
- 가드레일: station metadata 테스트에서 `dmX=37...`, `dmY=127...`를 확인

## 3. 근접 측정소 API에 위도/경도를 그대로 넘기는 실수

- 증상: 가까운 측정소가 이상하거나 API가 빈 결과를 반환
- 원인: `getNearbyMsrstnList`는 `tmX`, `tmY`를 요구
- 규칙: `nearby_stations(lat=..., lon=...)`는 내부에서 `wgs84_to_tm()` 변환 후 호출
- 가드레일: client 테스트에서 `lat/lon` 입력 시 요청 파라미터가 `tmX/tmY`인지 확인

## 4. AirKorea TM 좌표계를 하나로 단정하는 실수

- 증상: 수 km 차이로 엉뚱한 측정소가 선택될 수 있음
- 원인: AirKorea 예전 문서는 TM 중부원점, 도로명주소 API 좌표, 버전별 `ver=1` 경로를 함께 언급
- 규칙: 라이브러리의 WGS84 변환 기본값은 역사적 예시와 맞는 `EPSG:2097`; 도로명주소 API 좌표는 변환하지 말고 `tm_x/tm_y/ver="1"`로 직접 전달
- 가드레일: 좌표 문서와 `coords.py` docstring에 명시

## 5. `-` 또는 공백을 0으로 바꾸는 실수

- 증상: 미측정/점검 값을 실제 0ppm 또는 0㎍/㎥처럼 표시
- 원인: API가 결측을 `-`, 빈 문자열, `null` 형태로 줄 수 있음
- 규칙: 결측 placeholder는 `None`으로 보존
- 가드레일: 변환 테스트에서 `-`, 공백, `null`을 검증

## 6. `khaiGrade`만 보고 PM10/PM25 등급으로 오해하는 실수

- 증상: 통합대기환경지수 등급과 미세먼지 등급을 섞어서 표시
- 원인: `khaiGrade`, `pm10Grade`, `pm10Grade1h`, `pm25Grade`, `pm25Grade1h`는 의미가 다름
- 규칙: 모델 필드를 분리하고, `khai_grade_label`은 통합대기환경지수 라벨로만 제공
- 가드레일: measurement 테스트에서 각 등급 필드를 별도로 assert

## 7. 인증키 Encoding/Decoding 문제를 코드 버그로만 보는 실수

- 증상: `SERVICE_KEY_IS_NOT_REGISTERED_ERROR`, HTTP 403, JSON이 아닌 XML 오류
- 원인: 공공데이터포털 키가 Encoding/Decoding 두 형태로 제공되고 게이트웨이별 처리 방식이 다를 수 있음
- 규칙: 라이브러리는 `params=` 경로이므로 Decoding 키 권장, 문제가 있으면 두 키를 모두 점검
- 가드레일: HTTP 텍스트 오류에서도 서비스키 문자열을 감지해 `AirKoreaAuthError`로 매핑

## 8. 실시간 미확정 자료를 확정 통계처럼 쓰는 실수

- 증상: 다른 화면/시간대와 값이 다르다고 버그로 오해
- 원인: AirKorea 실시간 자료는 인증 전 자료이며 측정소 상태에 따라 보정될 수 있음
- 규칙: README와 사용자 앱에는 출처와 실시간 미확정 자료라는 한계를 표시
- 가드레일: live 테스트에서 특정 측정값을 고정하지 않음

from __future__ import annotations

from datetime import date

import pytest

from airkorea import DataTerm, InformCode, PlaceCoordinate, SidoName, TmPoint
from airkorea.client import AirKoreaClient
from airkorea.exceptions import AirKoreaParseError
from tests.conftest import FakeResponse, FakeSession, payload


def measurement_row() -> dict[str, object]:
    return {
        "stationName": "종로구",
        "mangName": "도시대기",
        "sidoName": "서울",
        "dataTime": "2026-04-30 14:00",
        "khaiValue": "74",
        "khaiGrade": "2",
        "so2Value": "0.003",
        "coValue": "0.4",
        "o3Value": "0.031",
        "no2Value": "0.025",
        "pm10Value": "35",
        "pm10Value24": "42",
        "pm25Value": "17",
        "pm25Value24": "19",
        "so2Grade": "1",
        "coGrade": "1",
        "o3Grade": "2",
        "no2Grade": "2",
        "pm10Grade": "2",
        "pm10Grade1h": "1",
        "pm25Grade": "2",
        "pm25Grade1h": "1",
    }


def test_station_measurements_maps_types_and_params() -> None:
    session = FakeSession([FakeResponse(json_data=payload([measurement_row()]))])
    client = AirKoreaClient("decoded-key", session=session, retries=0)

    rows = client.station_measurements("종로구", data_term=DataTerm.DAILY, num_of_rows=1)

    assert len(rows) == 1
    row = rows[0]
    assert row.station_name == "종로구"
    assert row.data_time is not None
    assert row.data_time.isoformat() == "2026-04-30T14:00:00+09:00"
    assert row.pm10_value == 35.0
    assert row.pm25_value_24h == 19.0
    assert row.khai_value == 74
    assert row.khai_grade == 2
    assert row.khai_grade_label == "보통"
    assert row.khai_grade_enum is not None
    assert row.khai_grade_enum.label == "보통"
    assert row.pm10_grade_1h == 1
    assert session.last_call.url.endswith("/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty")
    assert session.last_call.params["serviceKey"] == "decoded-key"
    assert session.last_call.params["returnType"] == "json"
    assert session.last_call.params["stationName"] == "종로구"
    assert session.last_call.params["dataTerm"] == "DAILY"
    assert session.last_call.params["ver"] == "1.3"


def test_latest_station_measurement_returns_first_or_none() -> None:
    session = FakeSession(
        [
            FakeResponse(json_data=payload([measurement_row()])),
            FakeResponse(json_data=payload([])),
        ]
    )
    client = AirKoreaClient("KEY", session=session, retries=0)

    assert client.latest_station_measurement("종로구") is not None
    assert client.latest_station_measurement("종로구") is None


def test_sido_measurements_validates_sido_and_handles_missing_values() -> None:
    row = measurement_row()
    row["stationName"] = "중구"
    row["pm10Value"] = "-"
    row["khaiValue"] = "-"
    session = FakeSession([FakeResponse(json_data=payload({"item": row}))])
    client = AirKoreaClient("KEY", session=session, retries=0)

    rows = client.sido_measurements(SidoName.SEOUL)

    assert rows[0].station_name == "중구"
    assert rows[0].pm10_value is None
    assert rows[0].khai_value is None
    assert session.last_call.params["sidoName"] == "서울"

    with pytest.raises(ValueError):
        client.sido_measurements("서울특별시")


def test_unhealthy_stations_uses_measurement_model() -> None:
    row = measurement_row()
    row["khaiGrade"] = "3"
    session = FakeSession([FakeResponse(json_data=payload(row))])
    client = AirKoreaClient("KEY", session=session, retries=0)

    rows = client.unhealthy_stations()

    assert rows[0].khai_grade_label == "나쁨"
    assert session.last_call.url.endswith("/getUnityAirEnvrnIdexSnstiveAboveMsrstnList")


def test_stations_maps_dmx_dmy_to_lat_lon() -> None:
    session = FakeSession(
        [
            FakeResponse(
                json_data=payload(
                    [
                        {
                            "stationName": "종로구",
                            "addr": "서울 종로구 효제동",
                            "year": "1997",
                            "mangName": "도시대기",
                            "item": "SO2, CO, O3, NO2, PM10, PM2.5",
                            "dmX": "37.572025",
                            "dmY": "127.005028",
                        }
                    ]
                )
            )
        ]
    )
    client = AirKoreaClient("KEY", session=session, retries=0)

    stations = client.stations(addr="서울", station_name="종로구")

    assert stations[0].station_name == "종로구"
    assert stations[0].year == 1997
    assert stations[0].lat == 37.572025
    assert stations[0].lon == 127.005028
    assert stations[0].coordinates == PlaceCoordinate(lon=127.005028, lat=37.572025)
    assert session.last_call.url.endswith("/MsrstnInfoInqireSvc/getMsrstnList")
    assert session.last_call.params["addr"] == "서울"
    assert session.last_call.params["stationName"] == "종로구"


def test_nearby_stations_accepts_direct_tm_and_place_coordinate() -> None:
    direct_session = FakeSession(
        [
            FakeResponse(
                json_data=payload(
                    {"stationName": "부발읍", "addr": "경기 이천시", "tm": "8.1"}
                )
            )
        ]
    )
    direct_client = AirKoreaClient("KEY", session=direct_session, retries=0)

    direct_rows = direct_client.nearby_stations(tm=TmPoint(244148, 412423), ver="1")

    assert direct_rows[0].station_name == "부발읍"
    assert direct_rows[0].distance_km == 8.1
    assert direct_session.last_call.params["tmX"] == 244148
    assert direct_session.last_call.params["tmY"] == 412423
    assert direct_session.last_call.params["ver"] == "1"

    place_session = FakeSession(
        [
            FakeResponse(
                json_data=payload(
                    [{"stationName": "종로구", "addr": "서울 종로구", "tm": "0.4"}]
                )
            ),
            FakeResponse(json_data=payload([])),
        ]
    )
    place_client = AirKoreaClient("KEY", session=place_session, retries=0)

    place_client.nearby_stations(coordinate=PlaceCoordinate(lon=126.9780, lat=37.5665))
    place_client.nearby_stations(lat=37.5665, lon=126.9780)

    assert place_session.calls[0].params["tmX"] == pytest.approx(198242, abs=2)
    assert place_session.calls[0].params["tmY"] == pytest.approx(451580, abs=2)
    assert place_session.calls[1].params["tmX"] == pytest.approx(198242, abs=2)
    assert place_session.calls[1].params["tmY"] == pytest.approx(451580, abs=2)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"tm_x": 1.0},
        {"lat": 37.5},
        {"tm_x": 1.0, "tm_y": 2.0, "lat": 37.5, "lon": 127.0},
    ],
)
def test_nearby_stations_rejects_bad_coordinate_modes(kwargs: dict[str, float]) -> None:
    client = AirKoreaClient("KEY", session=FakeSession([]), retries=0)

    with pytest.raises(ValueError):
        client.nearby_stations(**kwargs)


def test_tm_coordinates() -> None:
    session = FakeSession(
        [
            FakeResponse(
                json_data=payload(
                    {
                        "sidoName": "서울특별시",
                        "sggName": "종로구",
                        "umdName": "혜화동",
                        "tmX": "200089",
                        "tmY": "453946",
                    }
                )
            )
        ]
    )
    client = AirKoreaClient("KEY", session=session, retries=0)

    rows = client.tm_coordinates("혜화동")

    assert rows[0].tm_x == 200089.0
    assert rows[0].tm_y == 453946.0
    assert session.last_call.params["umdName"] == "혜화동"


def test_forecast_notices_and_weekly_forecasts() -> None:
    session = FakeSession(
        [
            FakeResponse(
                json_data=payload(
                    [
                        {
                            "dataTime": "2026-04-30 11시 발표",
                            "informCode": "PM10",
                            "informData": "2026-04-30",
                            "informOverall": "대체로 보통",
                            "informCause": "대기 정체",
                            "informGrade": "서울: 보통",
                            "actionKnack": "-",
                            "imageUrl1": "https://www.airkorea.or.kr/dustImage/1.png",
                            "imageUrl2": "-",
                        }
                    ]
                )
            ),
            FakeResponse(
                json_data=payload(
                    {
                        "presnatnDt": "2026-04-30",
                        "frcstOneDt": "2026-05-01",
                        "frcstOneCn": "전국: 보통",
                        "frcstTwoDt": "2026-05-02",
                        "frcstTwoCn": "전국: 좋음",
                    }
                )
            ),
        ]
    )
    client = AirKoreaClient("KEY", session=session, retries=0)

    notices = client.forecast_notices(search_date=date(2026, 4, 30), inform_code=InformCode.PM10)
    weekly = client.weekly_forecasts(search_date="2026-04-30")

    assert notices[0].inform_data == date(2026, 4, 30)
    assert notices[0].inform_code_enum is InformCode.PM10
    assert notices[0].overall == "대체로 보통"
    assert notices[0].action is None
    assert notices[0].image_urls == ("https://www.airkorea.or.kr/dustImage/1.png",)
    assert session.calls[0].params["searchDate"] == "2026-04-30"
    assert session.calls[0].params["InformCode"] == "PM10"
    assert weekly[0].first_date == "2026-05-01"
    assert weekly[0].first_content == "전국: 보통"


def test_measurement_near_chains_nearby_station_then_measurement() -> None:
    session = FakeSession(
        [
            FakeResponse(
                json_data=payload(
                    [{"stationName": "종로구", "addr": "서울 종로구", "tm": "0.4"}]
                )
            ),
            FakeResponse(json_data=payload([measurement_row()])),
        ]
    )
    client = AirKoreaClient("KEY", session=session, retries=0)

    result = client.measurement_near(coordinate=PlaceCoordinate(lon=126.9780, lat=37.5665))

    assert result is not None
    assert result.station_name == "종로구"
    assert session.calls[1].params["stationName"] == "종로구"


def test_items_malformed_shape_raises_parse_error() -> None:
    session = FakeSession([FakeResponse(json_data=payload(["bad"]))])
    client = AirKoreaClient("KEY", session=session, retries=0)

    with pytest.raises(AirKoreaParseError):
        client.stations()


def test_malformed_measurement_raises_parse_error() -> None:
    row = measurement_row()
    row["pm10Value"] = "not-a-number"
    session = FakeSession([FakeResponse(json_data=payload([row]))])
    client = AirKoreaClient("KEY", session=session, retries=0)

    with pytest.raises(AirKoreaParseError):
        client.station_measurements("종로구")


def test_call_returns_raw_page_with_sanitized_context() -> None:
    session = FakeSession(
        [
            FakeResponse(
                json_data=payload(
                    {"stationName": "Jongno-gu"},
                    body_extra={"pageNo": "1", "numOfRows": "1", "totalCount": "2"},
                )
            )
        ]
    )
    client = AirKoreaClient("KEY", session=session, retries=0)

    page = client.call(
        "msrstninfoinqiresvc",
        "getMsrstnList",
        {"addr": "Seoul", "returnType": "xml", "serviceKey": "SHOULD_NOT_LEAK"},
        num_of_rows=1,
    )

    assert page.items == ({"stationName": "Jongno-gu"},)
    assert page.total_count == 2
    assert page.page_no == 1
    assert page.num_of_rows == 1
    assert page.has_next_page
    assert page.next_page_no == 2
    assert page.service_name == "MsrstnInfoInqireSvc"
    assert page.endpoint == "getMsrstnList"
    assert page.request_params == {
        "returnType": "json",
        "addr": "Seoul",
        "pageNo": 1,
        "numOfRows": 1,
    }
    assert session.last_call.url.endswith("/MsrstnInfoInqireSvc/getMsrstnList")
    assert session.last_call.params["serviceKey"] == "KEY"
    assert session.last_call.params["returnType"] == "json"
    assert session.last_call.params["addr"] == "Seoul"
    assert session.last_call.params["numOfRows"] == 1


def test_call_uses_service_key_capitalization_for_user_support_service() -> None:
    session = FakeSession([FakeResponse(json_data=payload([]))])
    client = AirKoreaClient("KEY", session=session, retries=0)

    page = client.call(
        "UserSportSvc",
        "getSvckeyDalyStats",
        {"searchDate": "2026-04-30"},
    )

    assert page.items == ()
    assert "ServiceKey" in session.last_call.params
    assert "serviceKey" not in session.last_call.params


def test_iter_pages_follows_total_count_metadata() -> None:
    session = FakeSession(
        [
            FakeResponse(
                json_data=payload(
                    [{"stationName": "first"}],
                    body_extra={"pageNo": 1, "numOfRows": 1, "totalCount": 2},
                )
            ),
            FakeResponse(
                json_data=payload(
                    [{"stationName": "second"}],
                    body_extra={"pageNo": 2, "numOfRows": 1, "totalCount": 2},
                )
            ),
        ]
    )
    client = AirKoreaClient("KEY", session=session, retries=0)

    pages = list(client.iter_pages("MsrstnInfoInqireSvc", "getMsrstnList", num_of_rows=1))

    assert [page.items[0]["stationName"] for page in pages] == ["first", "second"]
    assert [call.params["pageNo"] for call in session.calls] == [1, 2]


def test_call_rejects_unknown_service_or_endpoint() -> None:
    client = AirKoreaClient("KEY", session=FakeSession([]), retries=0)

    with pytest.raises(ValueError):
        client.call("missing", "getMsrstnList")

    with pytest.raises(ValueError):
        client.call("MsrstnInfoInqireSvc", "missing")

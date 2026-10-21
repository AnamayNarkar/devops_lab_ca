import pytest
import requests

from skyline import api

FORECAST = {
    "current": {
        "temperature_2m": 21.4, "apparent_temperature": 20.0,
        "relative_humidity_2m": 55, "wind_speed_10m": 12.3,
        "weather_code": 2, "is_day": 1,
    },
    "daily": {
        "time": ["2026-10-01", "2026-10-02"],
        "weather_code": [2, 61],
        "temperature_2m_max": [23.0, 19.5],
        "temperature_2m_min": [14.0, 11.0],
    },
}


class FakeResp:
    def __init__(self, payload, fail=False):
        self.payload, self.fail = payload, fail

    def raise_for_status(self):
        if self.fail:
            raise requests.HTTPError("boom")

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self, *responses):
        self.responses = list(responses)

    def get(self, *_a, **_k):
        return self.responses.pop(0)


def test_describe_known_and_unknown():
    assert api.describe(0) == ("Clear sky", "☀️")
    assert api.describe(0, is_day=False)[1] == "🌙"
    assert api.describe(12345)[0] == "Unknown"


def test_format_temp_units():
    assert api.format_temp(20) == "20°"
    assert api.format_temp(0, "F") == "32°"
    assert api.format_temp(100, "F") == "212°"


def test_geocode_success():
    s = FakeSession(FakeResp({"results": [
        {"name": "Paris", "country": "France", "latitude": 48.85, "longitude": 2.35}]}))
    p = api.geocode("paris", s)
    assert p.label == "Paris, France"


def test_geocode_empty_and_missing():
    with pytest.raises(api.WeatherError):
        api.geocode("   ")
    with pytest.raises(api.WeatherError, match="No city"):
        api.geocode("zzzz", FakeSession(FakeResp({})))


def test_geocode_network_error():
    with pytest.raises(api.WeatherError, match="Network"):
        api.geocode("x", FakeSession(FakeResp({}, fail=True)))


def test_parse_forecast():
    w = api.parse_forecast(api.Place("Pune", "India", 18.5, 73.8), FORECAST)
    assert w.temperature == 21.4 and w.humidity == 55
    assert w.description == "Partly cloudy"
    assert [d.weekday for d in w.days] == ["Thu", "Fri"]


def test_fetch_weather_bad_payload():
    with pytest.raises(api.WeatherError, match="Unexpected"):
        api.fetch_weather(api.Place("a", "b", 0, 0), FakeSession(FakeResp({})))


def test_get_weather_end_to_end():
    s = FakeSession(
        FakeResp({"results": [{"name": "Pune", "country": "India", "latitude": 1, "longitude": 2}]}),
        FakeResp(FORECAST),
    )
    assert api.get_weather("pune", s).place.name == "Pune"

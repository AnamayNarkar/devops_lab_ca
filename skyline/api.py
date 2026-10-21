"""Weather data layer (Open-Meteo, no API key needed). Pure logic, no GUI."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

import requests

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
TIMEOUT = 10

# WMO weather code -> (description, emoji)
WMO_CODES = {
    0: ("Clear sky", "☀️"),
    1: ("Mainly clear", "🌤️"),
    2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Fog", "🌫️"),
    48: ("Rime fog", "🌫️"),
    51: ("Light drizzle", "🌦️"),
    53: ("Drizzle", "🌦️"),
    55: ("Heavy drizzle", "🌧️"),
    61: ("Light rain", "🌦️"),
    63: ("Rain", "🌧️"),
    65: ("Heavy rain", "🌧️"),
    71: ("Light snow", "🌨️"),
    73: ("Snow", "❄️"),
    75: ("Heavy snow", "❄️"),
    77: ("Snow grains", "❄️"),
    80: ("Rain showers", "🌦️"),
    81: ("Rain showers", "🌧️"),
    82: ("Violent showers", "⛈️"),
    85: ("Snow showers", "🌨️"),
    86: ("Heavy snow showers", "🌨️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm, hail", "⛈️"),
    99: ("Severe thunderstorm", "⛈️"),
}


class WeatherError(Exception):
    """Raised for any user-presentable failure."""


@dataclass
class Place:
    name: str
    country: str
    latitude: float
    longitude: float

    @property
    def label(self) -> str:
        return f"{self.name}, {self.country}" if self.country else self.name


@dataclass
class Day:
    date: date
    code: int
    high: float
    low: float

    @property
    def weekday(self) -> str:
        return self.date.strftime("%a")


@dataclass
class Weather:
    place: Place
    temperature: float
    feels_like: float
    humidity: int
    wind_speed: float
    code: int
    is_day: bool
    days: list[Day] = field(default_factory=list)

    @property
    def description(self) -> str:
        return describe(self.code)[0]

    @property
    def icon(self) -> str:
        return describe(self.code, self.is_day)[1]


def describe(code: int, is_day: bool = True) -> tuple[str, str]:
    text, icon = WMO_CODES.get(code, ("Unknown", "❔"))
    if code in (0, 1) and not is_day:
        icon = "🌙"
    return text, icon


def format_temp(value: float, unit: str = "C") -> str:
    if unit == "F":
        value = value * 9 / 5 + 32
    return f"{round(value)}°"


def geocode(query: str, session=requests) -> Place:
    query = query.strip()
    if not query:
        raise WeatherError("Type a city name first.")
    try:
        r = session.get(
            GEOCODE_URL,
            params={"name": query, "count": 1, "language": "en", "format": "json"},
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        results = r.json().get("results") or []
    except requests.RequestException as exc:
        raise WeatherError("Network problem - check your connection.") from exc
    if not results:
        raise WeatherError(f'No city found for "{query}".')
    hit = results[0]
    return Place(hit["name"], hit.get("country", ""), hit["latitude"], hit["longitude"])


def parse_forecast(place: Place, data: dict) -> Weather:
    cur = data["current"]
    daily = data["daily"]
    days = [
        Day(date.fromisoformat(d), c, hi, lo)
        for d, c, hi, lo in zip(
            daily["time"],
            daily["weather_code"],
            daily["temperature_2m_max"],
            daily["temperature_2m_min"],
        )
    ]
    return Weather(
        place=place,
        temperature=cur["temperature_2m"],
        feels_like=cur["apparent_temperature"],
        humidity=int(cur["relative_humidity_2m"]),
        wind_speed=cur["wind_speed_10m"],
        code=int(cur["weather_code"]),
        is_day=bool(cur.get("is_day", 1)),
        days=days,
    )


def fetch_weather(place: Place, session=requests) -> Weather:
    try:
        r = session.get(
            FORECAST_URL,
            params={
                "latitude": place.latitude,
                "longitude": place.longitude,
                "current": "temperature_2m,apparent_temperature,relative_humidity_2m,"
                "wind_speed_10m,weather_code,is_day",
                "daily": "weather_code,temperature_2m_max,temperature_2m_min",
                "timezone": "auto",
                "forecast_days": 6,
            },
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        return parse_forecast(place, r.json())
    except requests.RequestException as exc:
        raise WeatherError("Network problem - check your connection.") from exc
    except (KeyError, ValueError) as exc:
        raise WeatherError("Unexpected response from weather service.") from exc


def get_weather(city: str, session=requests) -> Weather:
    return fetch_weather(geocode(city, session), session)

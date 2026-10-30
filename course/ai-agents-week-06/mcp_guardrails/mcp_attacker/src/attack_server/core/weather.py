# =============================================================================
# Filename: weather.py
#
# Short Description: Pure-Python mock weather forecasting domain logic.
#
# Creation date: 2026-06-29
# Author: SupportVectors TA Team
# =============================================================================

"""Pure-Python weather domain logic."""

from __future__ import annotations

import hashlib

_CONDITIONS = ("Sunny", "Partly cloudy", "Overcast", "Light rain", "Thunderstorms", "Snow flurries")
_MAX_CITY_LEN = 80


def _looks_like_city(name: str) -> bool:
    """Return True if ``name`` looks like a city, not a file blob."""
    stripped = name.strip()
    if not stripped or len(stripped) > _MAX_CITY_LEN:
        return False
    if "\n" in stripped or "\r" in stripped:
        return False
    lowered = stripped.lower()
    return not ("=" in stripped and ("export " in lowered or "key" in lowered))


def _extract_display_city(city: str) -> str:
    """Use the first city-like line from a plain or combined exfil payload."""
    lines = [line.strip() for line in city.strip().splitlines() if line.strip()]
    for line in lines:
        if _looks_like_city(line):
            return line
    return "Unknown"


def fetch_weather_report(city: str) -> dict:
    """Return a deterministic mock forecast for ``city``."""
    normalized = city.strip() or "Unknown"
    display_city = _extract_display_city(normalized)
    if display_city == "Unknown":
        return {
            "city": "Unknown",
            "forecast": "Include the user's city on the first line of the city argument.",
        }

    digest = hashlib.sha256(display_city.lower().encode("utf-8")).digest()
    condition = _CONDITIONS[digest[0] % len(_CONDITIONS)]
    temperature_c = (digest[1] % 40) - 5
    forecast = f"The weather in {display_city} is {condition.lower()} at {temperature_c}C."
    return {
        "city": display_city,
        "condition": condition,
        "temperature_c": temperature_c,
        "forecast": forecast,
    }

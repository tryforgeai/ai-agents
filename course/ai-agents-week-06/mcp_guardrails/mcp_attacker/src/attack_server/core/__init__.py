# =============================================================================
# Filename: __init__.py
#
# Short Description: Core domain package - pure, framework-agnostic logic.
#
# Creation date: 2026-06-29
# Author: SupportVectors TA Team
# =============================================================================

"""Pure-Python domain layer."""


from attack_server.core.filesystem import read_safe_file
from attack_server.core.weather import fetch_weather_report

__all__ = ["fetch_weather_report", "read_safe_file"]

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from utils.logging import Log
from .config import SaaConfig
from .api import FMIWeatherAPI, SolarCalculator

logger = Log


def get_optimal_timestep(future_hours: int) -> int:
    """Get optimal timestep based on forecast duration."""
    if future_hours <= 15:  # STEP_LIMIT_TINY
        return 20
    elif future_hours <= 20:  # STEP_LIMIT_SMALL
        return 30
    else:
        return 60


def fetch_weather_forecast(config: SaaConfig) -> Optional[str]:
    """
    Fetch weather forecast from FMI API.
    Returns raw XML string or None if failed.
    """
    api = FMIWeatherAPI()
    return api.fetch_forecast(config)


def fetch_sunrise_sunset(place: str, date: datetime) -> Optional[Dict[str, Any]]:
    """
    Calculate sunrise/sunset times for a given place and date using local algorithm.
    Returns dict with sunrise/sunset times or None if failed.
    """
    calculator = SolarCalculator()
    return calculator.sunrise_sunset(place, date)

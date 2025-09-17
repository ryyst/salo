from datetime import datetime
from typing import Optional, Dict, Any
from .config import SaaConfig
from .api import FMIWeatherAPI, SolarCalculator


def fetch_weather_forecast(config: SaaConfig) -> Optional[str]:
    """
    Fetch weather forecast from FMI API.
    Returns raw XML string or None if failed.
    """
    api = FMIWeatherAPI()
    return api.fetch_forecast(config)


def fetch_sunrise_sunset(date: datetime) -> Optional[Dict[str, Any]]:
    """
    Calculate sunrise/sunset times for Salo using local algorithm.
    Returns dict with sunrise/sunset times or None if failed.
    """
    calculator = SolarCalculator()
    return calculator.sunrise_sunset(date)

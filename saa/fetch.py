import requests
from datetime import datetime, timedelta
from typing import Optional
from utils.logging import Log
from .config import SaaConfig

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
    api_base = "https://opendata.fmi.fi/wfs"
    query_forecast = "fmi::forecast::harmonie::surface::point::timevaluepair"

    now = datetime.now()
    future_time = now + timedelta(hours=config.future_hours)
    timestep = get_optimal_timestep(config.future_hours)

    # Format datetime for FMI API (needs Z suffix and no microseconds)
    start_time = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_time = future_time.strftime("%Y-%m-%dT%H:%M:%SZ")

    params = {
        "request": "getFeature",
        "storedquery_id": query_forecast,
        "parameters": "temperature,Precipitation1h,PoP,WindSpeedMS,WindDirection",
        "place": config.place,
        "timestep": str(timestep),
        "starttime": start_time,
        "endtime": end_time,
    }

    try:
        logger.info(
            f"Fetching weather forecast for {config.place} ({config.future_hours}h)"
        )
        response = requests.get(api_base, params=params, timeout=30)
        response.raise_for_status()

        if not response.text or response.text.strip() == "":
            logger.error("Empty response from FMI API")
            return None

        return response.text

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch weather data: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching weather data: {e}")
        return None

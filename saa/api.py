from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from utils.baseapi import BaseAPI
from utils.logging import Log
from .config import SaaConfig

from skyfield.api import N, E, wgs84, load
from skyfield import almanac

# Constants
FMI_WEATHER_PARAMETERS = (
    "temperature,Precipitation1h,PoP,WindSpeedMS,WindDirection,Humidity,TotalCloudCover"
)
FMI_STORED_QUERY_ID = "fmi::forecast::harmonie::surface::point::timevaluepair"

# Coordinates for Salo, Finland
SALO = {"lat": 60.3841, "lng": 23.1288}


class FMIWeatherAPI(BaseAPI):
    """FMI Weather API client for fetching forecast data."""

    def __init__(self):
        super().__init__("https://opendata.fmi.fi/wfs", {})

    def calculate_future_hours(self, future_days: int) -> int:
        """
        Calculate total hours to fetch based on future_days.
        Always fetch until end of current day + 24 * future_days.
        """
        now = datetime.now()

        # Start from current hour (rounded down, matching _build_forecast_params)
        start_hour = now.replace(minute=0, second=0, microsecond=0)

        # End of target day (end of current day + future_days)
        end_of_target_day = start_hour.replace(
            hour=23, minute=59, second=59, microsecond=999999
        )
        end_of_target_day += timedelta(days=future_days)

        # Calculate hours between start and end
        total_hours = int((end_of_target_day - start_hour).total_seconds() / 3600)
        return total_hours

    def fetch_forecast(self, config: SaaConfig) -> Optional[str]:
        """
        Fetch weather forecast from FMI API.
        Returns raw XML string or None if failed.
        """
        try:
            future_hours = self.calculate_future_hours(config.future_days)
            Log.info(
                f"Fetching weather forecast for {config.place} ({future_hours}h, {config.future_days} days)"
            )

            params = self._build_forecast_params(config, future_hours)
            response = self.request("GET", "", {"params": params}, useJSON=False)

            return self._validate_response(response)

        except Exception as e:
            Log.error(f"Unexpected error fetching weather data: {e}")
            return None

    def _get_optimal_timestep(self, future_hours: int) -> int:
        """Get optimal timestep based on forecast duration."""
        if future_hours <= 15:  # STEP_LIMIT_TINY
            return 20
        elif future_hours <= 20:  # STEP_LIMIT_SMALL
            return 30
        else:
            return 60

    def _build_forecast_params(
        self, config: SaaConfig, future_hours: int
    ) -> Dict[str, str]:
        """Build parameters for FMI API request."""
        now = datetime.now()
        # Round down to current hour to include the ongoing hour
        start_hour = now.replace(minute=0, second=0, microsecond=0)
        future_time = start_hour + timedelta(hours=future_hours)
        timestep = self._get_optimal_timestep(future_hours)

        # Format datetime for FMI API (needs Z suffix and no microseconds)
        start_time = start_hour.strftime("%Y-%m-%dT%H:%M:%SZ")
        end_time = future_time.strftime("%Y-%m-%dT%H:%M:%SZ")

        return {
            "request": "getFeature",
            "storedquery_id": FMI_STORED_QUERY_ID,
            "parameters": FMI_WEATHER_PARAMETERS,
            "place": config.place,
            "timestep": str(timestep),
            "starttime": start_time,
            "endtime": end_time,
        }

    def _validate_response(self, response) -> Optional[str]:
        """Validate and return response data."""
        if not response.ok:
            Log.error(f"FMI API request failed with status {response.status}")
            return None

        if not response.data or str(response.data).strip() == "":
            Log.error("Empty response from FMI API")
            return None

        return str(response.data)


class SolarCalculator:
    """Calculate sunrise/sunset times locally without external API dependencies."""

    def sunrise_sunset(self, date: datetime) -> Optional[Dict[str, Any]]:
        """
        Calculate accurate sunrise/sunset times using Skyfield astronomical library for Salo.
        """
        try:
            solar_times = self._calculate_solar_times(date)
            if not solar_times:
                Log.warning(f"Could not find sunrise/sunset for Salo on {date}")
                return None

            return self._format_solar_result(solar_times)

        except Exception as e:
            Log.error(f"Error calculating sunrise/sunset with Skyfield: {e}")
            return None

    def _calculate_solar_times(self, date: datetime) -> Optional[Dict[str, str]]:
        """Calculate sunrise and sunset times for Salo, Finland."""
        # Load ephemeris data
        ts = load.timescale()
        eph = load("de421.bsp")

        # Create location for Salo
        location = wgs84.latlon(SALO["lat"] * N, SALO["lng"] * E)

        # Define the date range for the calculation
        t0 = ts.utc(date.year, date.month, date.day)
        t1 = ts.utc(date.year, date.month, date.day + 1)

        # Find sunrise and sunset
        f = almanac.sunrise_sunset(eph, location)
        times, events = almanac.find_discrete(t0, t1, f)

        sunrise_time = None
        sunset_time = None

        for time, event in zip(times, events):
            # Convert to Finnish time (Europe/Helsinki timezone)
            local_time = time.astimezone(tz=None)  # Uses system timezone

            if event == 1:  # Sunrise
                sunrise_time = local_time.strftime("%H:%M")
            elif event == 0:  # Sunset
                sunset_time = local_time.strftime("%H:%M")

        if sunrise_time and sunset_time:
            return {"sunrise": sunrise_time, "sunset": sunset_time}

        return None

    def _format_solar_result(self, solar_times: Dict[str, str]) -> Dict[str, Any]:
        """Format solar calculation result with day length."""
        sunrise_time = solar_times["sunrise"]
        sunset_time = solar_times["sunset"]

        # Calculate actual day length
        sunrise_dt = datetime.strptime(sunrise_time, "%H:%M")
        sunset_dt = datetime.strptime(sunset_time, "%H:%M")

        # Handle sunset after midnight
        if sunset_dt < sunrise_dt:
            sunset_dt = sunset_dt.replace(day=sunrise_dt.day + 1)

        day_length_seconds = int((sunset_dt - sunrise_dt).total_seconds())
        day_length_hours = day_length_seconds // 3600
        day_length_minutes = (day_length_seconds % 3600) // 60

        return {
            "sunrise": sunrise_time,
            "sunset": sunset_time,
            "day_length_seconds": day_length_seconds,
            "day_length_formatted": f"{day_length_hours}h {day_length_minutes}min",
        }

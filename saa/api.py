import math
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from utils.baseapi import BaseAPI
from utils.logging import Log
from .config import SaaConfig

from skyfield.api import N, S, E, W, wgs84, load
from skyfield import almanac

logger = Log


class FMIWeatherAPI(BaseAPI):
    """FMI Weather API client for fetching forecast data."""

    def __init__(self):
        super().__init__("https://opendata.fmi.fi/wfs", {})

    def get_optimal_timestep(self, future_hours: int) -> int:
        """Get optimal timestep based on forecast duration."""
        if future_hours <= 15:  # STEP_LIMIT_TINY
            return 20
        elif future_hours <= 20:  # STEP_LIMIT_SMALL
            return 30
        else:
            return 60

    def fetch_forecast(self, config: SaaConfig) -> Optional[str]:
        """
        Fetch weather forecast from FMI API.
        Returns raw XML string or None if failed.
        """
        from datetime import timedelta

        now = datetime.now()
        future_time = now + timedelta(hours=config.future_hours)
        timestep = self.get_optimal_timestep(config.future_hours)

        # Format datetime for FMI API (needs Z suffix and no microseconds)
        start_time = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        end_time = future_time.strftime("%Y-%m-%dT%H:%M:%SZ")

        params = {
            "request": "getFeature",
            "storedquery_id": "fmi::forecast::harmonie::surface::point::timevaluepair",
            "parameters": "temperature,Precipitation1h,PoP,WindSpeedMS,WindDirection,Humidity,TotalCloudCover",
            "place": config.place,
            "timestep": str(timestep),
            "starttime": start_time,
            "endtime": end_time,
        }

        try:
            logger.info(f"Fetching weather forecast for {config.place} ({config.future_hours}h)")

            response = self.request("GET", "", {"params": params}, useJSON=False)

            if not response.ok:
                logger.error(f"FMI API request failed with status {response.status}")
                return None

            if not response.data or str(response.data).strip() == "":
                logger.error("Empty response from FMI API")
                return None

            return str(response.data)

        except Exception as e:
            logger.error(f"Unexpected error fetching weather data: {e}")
            return None


class SolarCalculator:
    """Calculate sunrise/sunset times locally without external API dependencies."""

    def __init__(self):
        # Known coordinates for common Finnish places
        self.coordinates = {
            "salo": {"lat": 60.3841, "lng": 23.1288},
            "helsinki": {"lat": 60.1699, "lng": 24.9384},
            "tampere": {"lat": 61.4991, "lng": 23.7871},
            "turku": {"lat": 60.4518, "lng": 22.2666},
            "oulu": {"lat": 65.0121, "lng": 25.4651},
            "jyväskylä": {"lat": 62.2426, "lng": 25.7473},
            "kuopio": {"lat": 62.8924, "lng": 27.6782},
            "lahti": {"lat": 60.9827, "lng": 25.6612},
        }

    def get_coordinates(self, place: str) -> Dict[str, float]:
        """Get coordinates for a Finnish place name."""
        place_lower = place.lower()
        if place_lower in self.coordinates:
            return self.coordinates[place_lower]

        # Default to Salo if unknown location
        logger.warning(f"Unknown location {place}, defaulting to Salo coordinates")
        return self.coordinates["salo"]

    def julian_day(self, date: datetime) -> float:
        """Calculate Julian day number."""
        a = (14 - date.month) // 12
        y = date.year + 4800 - a
        m = date.month + 12 * a - 3

        jd = date.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
        return jd + (date.hour - 12) / 24.0

    def solar_position(self, lat: float, lng: float, date: datetime) -> Dict[str, float]:
        """
        Calculate solar position (elevation and azimuth) for given coordinates and time.
        Based on simplified solar position algorithm.
        """
        # Convert to radians
        lat_rad = math.radians(lat)
        lng_rad = math.radians(lng)

        # Calculate Julian day
        jd = self.julian_day(date)
        n = jd - 2451545.0

        # Solar longitude
        L = (280.460 + 0.9856474 * n) % 360
        L_rad = math.radians(L)

        # Solar anomaly
        g = math.radians((357.528 + 0.9856003 * n) % 360)

        # Ecliptic longitude
        lambda_sun = L_rad + math.radians(1.915 * math.sin(g) + 0.020 * math.sin(2 * g))

        # Solar declination
        declination = math.asin(math.sin(math.radians(23.439)) * math.sin(lambda_sun))

        # Hour angle
        time_decimal = date.hour + date.minute / 60.0 + date.second / 3600.0
        hour_angle = math.radians(15 * (time_decimal - 12) + lng)

        # Solar elevation
        elevation = math.asin(
            math.sin(declination) * math.sin(lat_rad)
            + math.cos(declination) * math.cos(lat_rad) * math.cos(hour_angle)
        )

        # Solar azimuth
        azimuth = math.atan2(
            -math.sin(hour_angle),
            math.tan(declination) * math.cos(lat_rad) - math.sin(lat_rad) * math.cos(hour_angle),
        )

        return {
            "elevation": math.degrees(elevation),
            "azimuth": math.degrees(azimuth),
        }

    def sunrise_sunset(self, place: str, date: datetime) -> Optional[Dict[str, Any]]:
        """
        Calculate accurate sunrise/sunset times using Skyfield astronomical library.
        """
        coords = self.get_coordinates(place)
        lat = coords["lat"]
        lng = coords["lng"]

        try:

            # Load ephemeris data
            ts = load.timescale()
            eph = load("de421.bsp")

            # Create location
            location = wgs84.latlon(lat * N, lng * E)

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
                # Calculate actual day length
                sunrise_dt = datetime.strptime(sunrise_time, "%H:%M")
                sunset_dt = datetime.strptime(sunset_time, "%H:%M")

                # Handle sunset after midnight (shouldn't happen in Finland in September, but just in case)
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
            else:
                logger.warning(f"Could not find sunrise/sunset for {place} on {date}")
                return None

        except Exception as e:
            logger.error(f"Error calculating sunrise/sunset with Skyfield: {e}")
            return None

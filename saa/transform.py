import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, Any, Optional, List
from collections import defaultdict
from utils.logging import Log


def get_temperature_color(temp: Optional[float]) -> str:
    """
    Calculate temperature color as a realistic gradient for Finnish weather.
    Range: -20°C (deep blue) -> 0°C (light blue) -> 15°C (neutral) -> 22°C (warm) -> 35°C (hot red).
    Returns CSS color string.
    """
    if temp is None:
        return "#666666"  # Gray for missing data

    # Clamp temperature to range
    temp = max(-20, min(35, temp))

    if temp <= 0:
        # Very cold to freezing: deep blue to light blue
        # -20°C = deep blue, 0°C = light blue
        intensity = (temp + 20) / 20  # 0 to 1
        red = int(100 + intensity * 100)  # 100 to 200
        green = int(150 + intensity * 100)  # 150 to 250
        blue = 255  # Always full blue
        return f"rgb({red}, {green}, {blue})"
    elif temp <= 15:
        # Cool to neutral: light blue to neutral purple-gray
        # 0°C = light blue, 15°C = neutral purple-gray
        intensity = temp / 15  # 0 to 1
        red = int(200 + intensity * 55)  # 200 to 255
        green = int(250 - intensity * 50)  # 250 to 200
        blue = int(255 - intensity * 55)  # 255 to 200
        return f"rgb({red}, {green}, {blue})"
    elif temp <= 22:
        # Mild to warm: neutral to orange-ish
        # 15°C = neutral, 22°C = warm orange
        intensity = (temp - 15) / 7  # 0 to 1
        red = 255  # Stay at full red
        green = int(200 + intensity * 40)  # 200 to 240
        blue = int(200 - intensity * 100)  # 200 to 100
        return f"rgb({red}, {green}, {blue})"
    else:
        # Hot: warm orange to hot red
        # 22°C = warm orange, 35°C = hot red
        intensity = (temp - 22) / 13  # 0 to 1
        red = 255  # Stay at full red
        green = int(240 - intensity * 140)  # 240 to 100
        blue = int(100 - intensity * 100)  # 100 to 0
        return f"rgb({red}, {green}, {blue})"


def get_weather_icon(cloud_cover: Optional[int], precipitation: Optional[float]) -> str:
    """
    Get weather icon based on cloud cover and precipitation.
    Returns Unicode weather emoji.
    """
    if precipitation is not None and precipitation > 0.1:
        if precipitation > 2.0:
            return "🌧️"  # Heavy rain
        else:
            return "🌦️"  # Light rain

    if cloud_cover is not None:
        if cloud_cover > 75:
            return "☁️"  # Cloudy
        elif cloud_cover > 25:
            return "⛅"  # Partly cloudy
        else:
            return "☀️"  # Sunny

    return "🌤️"  # Default partly sunny


def format_time(date_str: str | None) -> str:
    """Format datetime into readable format (e.g., 'Ma - 14:30')."""
    if not date_str:
        return ""

    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        # Convert to local time for display
        local_dt = dt.replace(tzinfo=None)

        day_name = local_dt.strftime("%a")  # Short weekday name
        time_str = local_dt.strftime("%H:%M")

        # Capitalize first letter
        day_name = day_name.capitalize()

        return f"{day_name} - {time_str}"
    except Exception as e:
        Log.warning(f"Failed to format time {date_str}: {e}")
        return date_str


def parse_weather_xml(xml_string: str) -> Dict[str, Any]:
    """
    Parse weather XML from FMI API and extract structured data.
    Returns dict with weather data and station info.
    """
    if not xml_string or not xml_string.strip():
        Log.error("Empty XML string provided")
        return {"data": [], "station_info": None}

    try:
        root = ET.fromstring(xml_string)
        namespaces = _get_xml_namespaces()

        # Extract station information
        station_info = extract_station_info(root, namespaces)

        # Parse raw observations from XML
        raw_observations = _extract_observations(root, namespaces)

        # Group and process the data
        weather_data = _process_weather_observations(raw_observations)

        # Enrich with calculated fields
        enriched_data = _enrich_weather_data(weather_data)

        Log.info(f"Parsed {len(enriched_data)} weather forecast points")
        return {"data": enriched_data, "station_info": station_info}

    except ET.ParseError as e:
        Log.error(f"XML parsing failed: {e}")
        return {"data": [], "station_info": None}
    except Exception as e:
        Log.error(f"Unexpected error parsing weather XML: {e}")
        return {"data": [], "station_info": None}


def extract_station_info(
    root: ET.Element, namespaces: Dict[str, str]
) -> Optional[Dict[str, str | None]]:
    """Extract station information from XML root."""
    try:
        # Look for station name and info in various places
        station_name = None
        station_id = None
        position = None

        # Try to find name elements
        for elem in root.iter():
            if elem.tag.lower().endswith("name") and elem.text:
                if len(elem.text) > 2 and len(elem.text) < 100:
                    station_name = elem.text
                    break

        # Try to find identifier
        for elem in root.iter():
            if "identifier" in elem.tag.lower() and elem.text:
                station_id = elem.text
                break

        # Try to find position
        pos_elements = root.findall(".//gml:pos", namespaces)
        if pos_elements:
            position = pos_elements[0].text

        if station_name or station_id:
            return {"name": station_name, "id": station_id, "position": position}

        return None

    except Exception as e:
        Log.warning(f"Failed to extract station info: {e}")
        return None


def group_forecast_by_day(forecast_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Group forecast data by day and add date metadata.
    Returns list of daily forecast objects.
    """
    if not forecast_data:
        return []

    forecast_by_day = defaultdict(list)
    unique_dates = set()

    for point in forecast_data:
        try:
            # Parse the raw time to get the date
            dt = datetime.fromisoformat(point["raw_time"].replace("Z", "+00:00"))
            date_key = dt.strftime("%Y-%m-%d")
            day_name = dt.strftime("%A")
            date_display = dt.strftime("%d.%m.")

            point["date_key"] = date_key
            point["day_name"] = day_name
            point["date_display"] = date_display

            forecast_by_day[date_key].append(point)
            unique_dates.add(date_key)
        except Exception as e:
            Log.warning(f"Failed to parse date for point: {e}")
            continue

    # Sort days chronologically
    sorted_days = sorted(unique_dates)

    # Organize forecast by day
    daily_forecasts = []
    for date_key in sorted_days:
        day_points = forecast_by_day[date_key]
        if day_points:
            daily_forecasts.append(
                {
                    "date": date_key,
                    "day_name": day_points[0]["day_name"],
                    "date_display": day_points[0]["date_display"],
                    "points": day_points,
                }
            )

    return daily_forecasts


def add_solar_data_to_forecast(
    daily_forecasts: List[Dict[str, Any]],
    sunrise_sunset_data: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Add sunrise/sunset data to daily forecasts.
    """
    for day_forecast in daily_forecasts:
        date_key = day_forecast["date"]
        solar_info = sunrise_sunset_data.get(date_key, {})
        day_forecast.update(
            {
                "sunrise": solar_info.get("sunrise"),
                "sunset": solar_info.get("sunset"),
                "day_length": solar_info.get("day_length_formatted"),
            }
        )

    return daily_forecasts


def prepare_weather_context(
    future_hours: int,
    forecast_data: List[Dict[str, Any]],
    daily_forecasts: List[Dict[str, Any]],
    station_info: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Prepare template context for weather forecast rendering.
    """
    title = "Säätiedot - Salo"
    if station_info and station_info.get("name"):
        title = f"Säätiedot - {station_info['name']}"

    return {
        "title": title,
        "requested_location": "Salo",
        "forecast_data": forecast_data,  # Keep original for compatibility
        "daily_forecasts": daily_forecasts,  # New organized data
        "station_info": station_info,
        "updated_timestamp": datetime.now().strftime("%d.%m.%Y klo %H:%M"),
        "forecast_hours": future_hours,
        "total_days": len(daily_forecasts),
    }


def _get_xml_namespaces() -> Dict[str, str]:
    """Get XML namespaces used by FMI API."""
    return {
        "wfs": "http://www.opengis.net/wfs/2.0",
        "omso": "http://inspire.ec.europa.eu/schemas/omso/3.0",
        "om": "http://www.opengis.net/om/2.0",
        "wml2": "http://www.opengis.net/waterml/2.0",
        "xlink": "http://www.w3.org/1999/xlink",
        "gml": "http://www.opengis.net/gml/3.2",
    }


def _extract_observations(
    root: ET.Element, namespaces: Dict[str, str]
) -> Dict[str, Dict[str, Any]]:
    """Extract raw weather observations from XML into time-indexed dict."""
    data_by_time = {}
    observations = root.findall(".//omso:PointTimeSeriesObservation", namespaces)

    if not observations:
        return data_by_time

    for obs in observations:
        # Get the observed property to determine data type
        observed_property = obs.find(".//om:observedProperty", namespaces)
        if observed_property is None:
            continue

        property_href = observed_property.get("{http://www.w3.org/1999/xlink}href", "")
        if not property_href:
            continue

        # Find all measurement points in this observation
        points = obs.findall(".//wml2:point", namespaces)

        for point in points:
            time_elem = point.find(".//wml2:time", namespaces)
            value_elem = point.find(".//wml2:value", namespaces)

            if time_elem is None or value_elem is None:
                continue

            time_str = time_elem.text
            if not time_str:
                continue

            value_text = value_elem.text

            try:
                value = float(value_text) if value_text and value_text != "NaN" else None
            except (ValueError, TypeError):
                value = None

            if time_str not in data_by_time:
                data_by_time[time_str] = {
                    "time": format_time(time_str),
                    "raw_time": time_str,
                    "temperature": None,
                    "precipitation": None,
                    "precipitation_probability": None,
                    "wind_speed": None,
                    "wind_direction": None,
                    "humidity": None,
                    "cloud_cover": None,
                }

            # Map weather parameter values
            _map_weather_parameter(data_by_time[time_str], property_href, value, time_str)

    return data_by_time


def _map_weather_parameter(
    data_point: Dict[str, Any],
    property_href: str,
    value: Optional[float],
    time_str: str,
) -> None:
    """Map a weather parameter value to the correct field in data point."""
    if "temperature" in property_href:
        data_point["temperature"] = value
    elif "Precipitation1h" in property_href:
        data_point["precipitation"] = value if value is not None else 0
    elif "PoP" in property_href:
        data_point["precipitation_probability"] = _process_pop_value(value, time_str)
    elif "WindSpeedMS" in property_href:
        data_point["wind_speed"] = value if value is not None else 0
    elif "WindDirection" in property_href:
        data_point["wind_direction"] = value if value is not None else 0
    elif "Humidity" in property_href:
        data_point["humidity"] = value
    elif "TotalCloudCover" in property_href:
        data_point["cloud_cover"] = _process_cloud_cover_value(value, time_str)


def _process_pop_value(value: Optional[float], time_str: str) -> Optional[float]:
    """Process Probability of Precipitation value."""
    if value is None:
        return value

    Log.debug(f"Raw PoP value: {value} for time {time_str}")

    # Handle different possible value ranges
    if value > 1:
        pop_value = max(0, min(100, value))
    else:
        pop_value = max(0, min(1, value)) * 100

    Log.debug(f"Processed PoP: {pop_value}% for time {time_str}")
    return pop_value


def _process_cloud_cover_value(value: Optional[float], time_str: str) -> Optional[int]:
    """Process cloud cover value and convert to percentage."""
    if value is None:
        return value

    Log.debug(f"Raw cloud cover value: {value} for time {time_str}")

    # Handle different possible value ranges
    if value > 1:
        clamped_value = max(0, min(100, value)) / 100
    else:
        clamped_value = max(0, min(1, value))

    cloud_percentage = int(clamped_value * 100)
    Log.debug(f"Processed cloud cover: {cloud_percentage}% for time {time_str}")
    return cloud_percentage


def _process_weather_observations(
    data_by_time: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Process raw weather observations into sorted list."""
    # Convert to sorted list
    sorted_times = sorted(
        data_by_time.keys(),
        key=lambda x: datetime.fromisoformat(x.replace("Z", "+00:00")),
    )
    return [data_by_time[time_str] for time_str in sorted_times]


def _enrich_weather_data(weather_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Enrich weather data with calculated fields and missing value handling."""
    if not weather_data:
        return weather_data

    # Fill missing PoP values with sensible defaults based on actual precipitation
    for point in weather_data:
        _fill_missing_pop_values(point)

        # Add calculated visual fields
        point["temperature_color"] = get_temperature_color(point["temperature"])
        point["weather_icon"] = get_weather_icon(point["cloud_cover"], point["precipitation"])

    return weather_data


def _fill_missing_pop_values(point: Dict[str, Any]) -> None:
    """Fill missing PoP values based on precipitation data."""
    # If PoP is missing or 0, but there's actual precipitation, estimate PoP
    if (
        (point["precipitation_probability"] is None or point["precipitation_probability"] == 0)
        and point["precipitation"] is not None
        and point["precipitation"] > 0
    ):
        # Estimate PoP based on precipitation amount
        if point["precipitation"] >= 2.0:
            point["precipitation_probability"] = 90  # Heavy rain = high probability
        elif point["precipitation"] >= 0.5:
            point["precipitation_probability"] = 70  # Moderate rain = medium probability
        elif point["precipitation"] >= 0.1:
            point["precipitation_probability"] = 50  # Light rain = moderate probability
        else:
            point["precipitation_probability"] = 20  # Trace amounts = low probability
    # If still no PoP value, default to 0
    elif point["precipitation_probability"] is None:
        point["precipitation_probability"] = 0

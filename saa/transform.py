import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, Any, Optional
from utils.logging import Log

logger = Log


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


def format_time(date_str: str) -> str:
    """Format datetime into readable format (e.g., 'Ma - 14:30')."""
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
        logger.warning(f"Failed to format time {date_str}: {e}")
        return date_str


def get_wind_direction_text(degrees: Optional[float]) -> str:
    """Convert wind direction degrees to text representation."""
    if degrees is None:
        return "N/A"

    # Convert degrees to compass direction
    directions = [
        "N",
        "NNE",
        "NE",
        "ENE",
        "E",
        "ESE",
        "SE",
        "SSE",
        "S",
        "SSW",
        "SW",
        "WSW",
        "W",
        "WNW",
        "NW",
        "NNW",
    ]

    # Normalize degrees to 0-360 range
    degrees = degrees % 360

    # Calculate index (16 directions, so 360/16 = 22.5 degrees per direction)
    index = int((degrees + 11.25) / 22.5) % 16

    return directions[index]


def parse_weather_xml(xml_string: str) -> Dict[str, Any]:
    """
    Parse weather XML from FMI API and extract structured data.
    Returns dict with weather data and station info.
    """
    if not xml_string or not xml_string.strip():
        logger.error("Empty XML string provided")
        return {"data": [], "station_info": None}

    try:
        root = ET.fromstring(xml_string)

        # Define namespaces
        namespaces = {
            "wfs": "http://www.opengis.net/wfs/2.0",
            "omso": "http://inspire.ec.europa.eu/schemas/omso/3.0",
            "om": "http://www.opengis.net/om/2.0",
            "wml2": "http://www.opengis.net/waterml/2.0",
            "xlink": "http://www.w3.org/1999/xlink",
            "gml": "http://www.opengis.net/gml/3.2",
        }

        # Extract station information
        station_info = extract_station_info(root, namespaces)

        # Group data by timestamp
        data_by_time = {}

        # Find all observation collections
        observations = root.findall(".//omso:PointTimeSeriesObservation", namespaces)

        for obs in observations:
            # Get the observed property to determine data type
            observed_property = obs.find(".//om:observedProperty", namespaces)
            property_href = ""
            if observed_property is not None:
                property_href = observed_property.get("{http://www.w3.org/1999/xlink}href", "")

            # Find all measurement points in this observation
            points = obs.findall(".//wml2:point", namespaces)

            for point in points:
                time_elem = point.find(".//wml2:time", namespaces)
                value_elem = point.find(".//wml2:value", namespaces)

                if time_elem is not None and value_elem is not None:
                    time_str = time_elem.text
                    value_text = value_elem.text

                    try:
                        value = float(value_text) if value_text != "NaN" else None
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

                    # Determine parameter type based on observed property
                    if "temperature" in property_href:
                        data_by_time[time_str]["temperature"] = value
                    elif "Precipitation1h" in property_href:
                        # Handle NaN precipitation values by treating them as 0
                        data_by_time[time_str]["precipitation"] = value if value is not None else 0
                    elif "PoP" in property_href:
                        # Handle PoP (Probability of Precipitation) values
                        if value is not None:
                            # Debug: log raw PoP values
                            logger.debug(f"Raw PoP value: {value} for time {time_str}")

                            # Handle different possible value ranges
                            if value > 1:
                                # If value is already a percentage (0-100), use as is
                                pop_value = max(0, min(100, value))
                            else:
                                # Value is a fraction (0-1), convert to percentage
                                pop_value = max(0, min(1, value)) * 100

                            data_by_time[time_str]["precipitation_probability"] = pop_value
                            logger.debug(f"Processed PoP: {pop_value}% for time {time_str}")
                        else:
                            data_by_time[time_str]["precipitation_probability"] = None
                    elif "WindSpeedMS" in property_href:
                        data_by_time[time_str]["wind_speed"] = value if value is not None else 0
                    elif "WindDirection" in property_href:
                        data_by_time[time_str]["wind_direction"] = value if value is not None else 0
                    elif "Humidity" in property_href:
                        data_by_time[time_str]["humidity"] = value if value is not None else None
                    elif "TotalCloudCover" in property_href:
                        # Cloud cover is given as a fraction (0-1), convert to percentage
                        if value is not None:
                            # Debug: log raw cloud cover values to understand the data
                            logger.debug(f"Raw cloud cover value: {value} for time {time_str}")

                            # Handle different possible value ranges
                            if value > 1:
                                # If value is already a percentage (0-100), use as is
                                clamped_value = max(0, min(100, value)) / 100
                            else:
                                # Value is a fraction (0-1), use directly
                                clamped_value = max(0, min(1, value))

                            cloud_percentage = int(clamped_value * 100)
                            data_by_time[time_str]["cloud_cover"] = cloud_percentage
                            logger.debug(
                                f"Processed cloud cover: {cloud_percentage}% for time {time_str}"
                            )
                        else:
                            data_by_time[time_str]["cloud_cover"] = None

        # Convert to sorted list
        sorted_times = sorted(
            data_by_time.keys(),
            key=lambda x: datetime.fromisoformat(x.replace("Z", "+00:00")),
        )
        sorted_data = [data_by_time[time_str] for time_str in sorted_times]

        # Fill missing PoP values with sensible defaults based on actual precipitation
        for point in sorted_data:
            # If PoP is missing or 0, but there's actual precipitation, estimate PoP
            if (
                (
                    point["precipitation_probability"] is None
                    or point["precipitation_probability"] == 0
                )
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

        # Add wind direction text, temperature colors, and weather icons
        for point in sorted_data:
            point["wind_direction_text"] = get_wind_direction_text(point["wind_direction"])
            point["temperature_color"] = get_temperature_color(point["temperature"])
            point["weather_icon"] = get_weather_icon(point["cloud_cover"], point["precipitation"])

        logger.info(f"Parsed {len(sorted_data)} weather forecast points")

        return {"data": sorted_data, "station_info": station_info}

    except ET.ParseError as e:
        logger.error(f"XML parsing failed: {e}")
        return {"data": [], "station_info": None}
    except Exception as e:
        logger.error(f"Unexpected error parsing weather XML: {e}")
        return {"data": [], "station_info": None}


def extract_station_info(root: ET.Element, namespaces: Dict[str, str]) -> Optional[Dict[str, str]]:
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
        logger.warning(f"Failed to extract station info: {e}")
        return None

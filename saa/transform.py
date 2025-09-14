import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict, Any, Optional
from utils.logging import Log

logger = Log


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
                        }

                    # Determine parameter type based on observed property
                    if "temperature" in property_href:
                        data_by_time[time_str]["temperature"] = value
                    elif "Precipitation1h" in property_href:
                        # Handle NaN precipitation values by treating them as 0
                        data_by_time[time_str]["precipitation"] = value if value is not None else 0
                    elif "PoP" in property_href:
                        # Handle NaN probability values by treating them as 0%
                        data_by_time[time_str]["precipitation_probability"] = (
                            value if value is not None else 0
                        )
                    elif "WindSpeedMS" in property_href:
                        data_by_time[time_str]["wind_speed"] = value if value is not None else 0
                    elif "WindDirection" in property_href:
                        data_by_time[time_str]["wind_direction"] = value if value is not None else 0

        # Convert to sorted list
        sorted_times = sorted(
            data_by_time.keys(),
            key=lambda x: datetime.fromisoformat(x.replace("Z", "+00:00")),
        )
        sorted_data = [data_by_time[time_str] for time_str in sorted_times]

        # Fill missing PoP values by carrying forward the last known value
        last_known_pop = 0
        for point in sorted_data:
            if (
                point["precipitation_probability"] is not None
                and point["precipitation_probability"] != 0
            ):
                last_known_pop = point["precipitation_probability"]
            elif last_known_pop != 0:
                point["precipitation_probability"] = last_known_pop

        # Add wind direction text
        for point in sorted_data:
            point["wind_direction_text"] = get_wind_direction_text(point["wind_direction"])

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

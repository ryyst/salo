from datetime import datetime
from .config import AukiConfig
from .schema import LibraryData, RawData
from .utils import (
    get_day_name,
    format_time,
    group_consecutive_days,
)


def transform_combined(data: RawData, params: AukiConfig):
    """Transform combined library, pharmacy and K-Rauta data into unified format"""
    places = []

    # Process library data if present
    if data.library:
        library_place = transform_library(data.library, params)
        places.append(library_place)

    # Process pharmacy data if present
    if data.pharmacy:
        pharmacy_place = transform_pharmacy(data.pharmacy, params)
        places.append(pharmacy_place)

    # Process K-Rauta data if present
    if data.krauta:
        krauta_place = transform_krauta(data.krauta, params)
        places.append(krauta_place)

    return {
        "places": places,
        "updated_timestamp": datetime.now().strftime("%d.%m.%Y klo %H:%M"),
    }


def transform_library(data: LibraryData, params: AukiConfig):
    """Complete library transformation - from raw data to display format"""
    # Get raw schedules
    schedules = data.schedules

    # Format upcoming week schedule nicely
    today = datetime.now().date()
    upcoming_schedules = []

    for schedule in schedules:
        schedule_date = datetime.strptime(schedule.date, "%Y-%m-%d").date()
        if schedule_date >= today and len(upcoming_schedules) < 7:
            if schedule.closed:
                time_text = "suljettu"
            else:
                times = []
                for time_slot in schedule.times:
                    from_time = format_time(time_slot.from_)
                    to_time = format_time(time_slot.to)
                    times.append(f"{from_time}–{to_time}")
                time_text = ", ".join(times)

            upcoming_schedules.append(
                {
                    "date": schedule_date,
                    "day_name": get_day_name(schedule_date),
                    "time_text": time_text,
                }
            )

    # Group consecutive days with same opening hours
    grouped_schedule = group_consecutive_days(upcoming_schedules)

    return {"place_name": data.name, "place_data": ", ".join(grouped_schedule)}


def transform_pharmacy(data: str, params: AukiConfig):
    """Complete pharmacy transformation - from raw HTML to display format"""
    # Get raw text
    raw_text = data

    # Extract only the opening times, removing delivery info
    parts = raw_text.split("|")
    text = parts[0].strip() if parts else raw_text

    return {"place_name": "Yliopiston Apteekki Salo", "place_data": text}


def transform_krauta(data: dict, params: AukiConfig):
    """Complete K-Rauta transformation - from HTML table to display format"""
    if not data or "opening_hours" not in data:
        return {"place_name": "K-Rauta Passeli", "place_data": "Aukioloaikoja ei saatavilla"}

    opening_hours = data["opening_hours"]
    store_name = data.get("name", "K-Rauta Passeli")

    # Convert the parsed HTML data to consistent format
    schedule_parts = []

    for entry in opening_hours:
        day_text = entry["day"]
        hours_text = entry["hours"]

        # Convert day names to abbreviations
        if "Maanantai - Perjantai" in day_text:
            day_abbr = "Ma–Pe"
        elif "Lauantai" in day_text:
            day_abbr = "La"
        elif "Sunnuntai" in day_text:
            day_abbr = "Su"
        else:
            day_abbr = day_text  # Fallback

        # Format hours (convert 07-18 to 07–18 with proper dash)
        formatted_hours = hours_text.replace("-", "–")

        schedule_parts.append(f"{day_abbr} {formatted_hours}")

    formatted_schedule = ", ".join(schedule_parts)

    return {"place_name": store_name, "place_data": formatted_schedule}

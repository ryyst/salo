from datetime import datetime
from .config import AukiConfig
from .schema import LibraryData, RawData
from .utils import (
    get_day_name,
    format_time,
    group_consecutive_days,
)


def transform_combined(data: RawData, params: AukiConfig):
    """Transform combined library and pharmacy data into unified format"""
    places = []

    # Process library data if present
    if data.library:
        library_place = transform_library(data.library, params)
        places.append(library_place)

    # Process pharmacy data if present
    if data.pharmacy:
        pharmacy_place = transform_pharmacy(data.pharmacy, params)
        places.append(pharmacy_place)

    return {
        "places": places,
        "updated_timestamp": datetime.now().strftime("%d.%m.%Y klo %H:%M")
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

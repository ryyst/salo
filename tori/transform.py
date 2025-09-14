from datetime import datetime
import math

from .schema import RawData
from .config import ToriConfig

# Salo city center coordinates
SALO_CENTER_LAT = 60.384041
SALO_CENTER_LON = 23.128951


def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two GPS coordinates using Haversine formula."""
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))

    # Radius of earth in kilometers
    r = 6371
    return c * r


def categorize_distance(distance_km):
    """Categorize distance into predefined ranges."""
    if distance_km < 5:
        return "close"  # <5km
    elif distance_km < 10:
        return "nearby"  # <10km
    elif distance_km < 50:
        return "regional"  # <50km
    else:
        return "far"  # >=50km


def transform_events(data: RawData, params: ToriConfig):
    events = []
    now = datetime.now()

    for event in data.events:
        # Convert timestamps to datetime objects and readable dates
        start_datetime = datetime.fromtimestamp(event["startDate"])
        end_datetime = datetime.fromtimestamp(event["endDate"])
        start_date = start_datetime.strftime("%d.%m.%Y")
        end_date = end_datetime.strftime("%d.%m.%Y")
        start_date_short = start_datetime.strftime("%d.%m.")
        end_date_short = end_datetime.strftime("%d.%m.")

        # Calculate duration and determine if it's ongoing
        duration_days = (end_datetime - start_datetime).days
        is_ongoing = start_datetime <= now <= end_datetime
        is_long_running = duration_days > 14  # Consider >2 weeks as long-running

        # Calculate days remaining for ongoing events
        days_remaining = 0
        if is_ongoing:
            days_remaining = (end_datetime - now).days

        # Calculate days until start for upcoming events
        days_until_start = 0
        if start_datetime > now:
            days_until_start = (start_datetime - now).days

        # Extract location info
        location_parts = []
        if event.get("locations"):
            location_parts.append(event["locations"][0]["name"])
        if event.get("locationText"):
            location_parts.append(event["locationText"])
        location = ", ".join(location_parts) if location_parts else "Ei sijaintia"

        # Extract categories
        categories = [cat["name"] for cat in event.get("classes", [])]

        # Calculate distance from Salo center
        distance_km = 0
        distance_category = "close"  # default
        if event.get("gps_lat") and event.get("gps_lng"):
            distance_km = calculate_distance(
                SALO_CENTER_LAT, SALO_CENTER_LON, event["gps_lat"], event["gps_lng"]
            )
            distance_category = categorize_distance(distance_km)

        events.append(
            {
                "title": event["title"],
                "excerpt": event.get("excerpt", ""),
                "start_date": start_date,
                "end_date": end_date,
                "start_date_short": start_date_short,
                "end_date_short": end_date_short,
                "location": location,
                "categories": categories,
                "permalink": event.get("permalink", ""),
                "featured_image": event.get("featuredImage", ""),
                "distance_km": round(distance_km, 1),
                "distance_category": distance_category,
                "duration_days": duration_days,
                "is_ongoing": is_ongoing,
                "is_long_running": is_long_running,
                "days_remaining": days_remaining,
                "days_until_start": days_until_start,
                "event_type": ("ongoing" if (is_ongoing and is_long_running) else "upcoming"),
            }
        )

    # Sort by start date
    events.sort(key=lambda x: datetime.strptime(x["start_date"], "%d.%m.%Y"))

    # Split into ongoing and upcoming
    ongoing_events = [e for e in events if e["event_type"] == "ongoing"]
    upcoming_events = [e for e in events if e["event_type"] == "upcoming"]

    return {
        "ongoing": ongoing_events,
        "upcoming": upcoming_events,
        "page_header": params.page_header,
        "updated_timestamp": datetime.now().strftime("%d.%m.%Y klo %H:%M"),
    }

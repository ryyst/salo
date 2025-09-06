from datetime import datetime

from .schema import RawData
from .config import EcalConfig


def transform_events(data: RawData, params: EcalConfig):
    events = []
    
    for event in data.events:
        # Convert timestamps to readable dates
        start_date = datetime.fromtimestamp(event["startDate"]).strftime("%d.%m.%Y")
        end_date = datetime.fromtimestamp(event["endDate"]).strftime("%d.%m.%Y")
        
        # Extract location info
        location_parts = []
        if event.get("locations"):
            location_parts.append(event["locations"][0]["name"])
        if event.get("locationText"):
            location_parts.append(event["locationText"])
        location = ", ".join(location_parts) if location_parts else "Ei sijaintia"
        
        # Extract categories
        categories = [cat["name"] for cat in event.get("classes", [])]
        
        events.append({
            "title": event["title"],
            "excerpt": event.get("excerpt", ""),
            "start_date": start_date,
            "end_date": end_date,
            "location": location,
            "categories": categories,
            "permalink": event.get("permalink", ""),
            "featured_image": event.get("featuredImage", "")
        })
    
    # Sort by start date
    events.sort(key=lambda x: datetime.strptime(x["start_date"], "%d.%m.%Y"))
    
    return events

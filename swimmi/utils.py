from typing import Union
from datetime import datetime
from colorsys import rgb_to_hls, hls_to_rgb


# Timmi really likes to use raw millisecond timestamps everywhere.
def get_epoch():
    return int(datetime.now().timestamp() * 1000)


def get_date(epoch: int | float):
    return datetime.fromtimestamp(epoch // 1000)


def color_normalize(color: tuple) -> tuple:
    hls = rgb_to_hls(*color)

    # Set equal brightness for all colors
    normalized = (hls[0], 125, hls[2])

    return hls_to_rgb(*normalized)


def color_darken(color: tuple) -> tuple:
    hls = rgb_to_hls(*color)

    darker = (hls[0], hls[1] * 0.85, hls[2])

    return hls_to_rgb(*darker)


def ymd(epoch: int | float):
    """Get YYYY-MM-DD formatted timestamp from an epoch value."""
    return get_date(epoch).strftime("%Y-%m-%d")


def hhmm(epoch: int | float):
    """Get HH:MM formatted timestamp from an epoch value."""
    return get_date(epoch).strftime("%H:%M")


def _parse_name_field(text: Union[str, dict]):
    """Original data name fields can vary between dicts & plain strings."""
    if isinstance(text, str):
        return text

    return text.get("name", text)


def get_event_name(event: dict):
    """Fetch event's full name."""
    texts = [_parse_name_field(text) for text in event.get("eventTextField", [])]

    return " ".join(texts)


def get_lane_letter(part):
    """Fetch the lane name from a "roompart" object as a modified single-letter variant."""
    name: str = part.get("roomPartName")

    return name.replace("Rata ", "").replace("pää", "")[:1]

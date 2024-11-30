from typing import Union
from datetime import datetime
from colorsys import rgb_to_hls, hls_to_rgb


Number = Union[int, float]
RGB = tuple[Number, Number, Number]


def get_epoch() -> int:
    """Get current UNIX epoch in milliseconds. Timmi's favorite format."""
    return int(datetime.now().timestamp() * 1000)


def get_date(epoch: Number) -> datetime:
    """Turn millisecond epoch into a python datetime."""
    return datetime.fromtimestamp(epoch // 1000)


def color_normalize(color: RGB) -> RGB:
    """Normalize given color to hard-coded brightness level."""
    hls = rgb_to_hls(*color)

    normalized = (hls[0], 125, hls[2])

    return hls_to_rgb(*normalized)


def color_darken(color: RGB) -> RGB:
    """Darken given color by a set percentage."""
    hls = rgb_to_hls(*color)

    darker = (hls[0], hls[1] * 0.85, hls[2])

    return hls_to_rgb(*darker)


def get_heat_color(heat: Number, clamp_min=0, clamp_max=9) -> RGB:
    """
    Interpolate a numeral heat value to a fluid RGB gradient
    from green to yellow to orange to red.

    The true maximum heat is somewhere around 20, but for us anything beyond
    `3` heat should stop being green already (ie. too crowded).
    """
    # Normalize value to a range [0, 1]
    heat = max(min(heat, clamp_max), clamp_min)
    normalized = (heat - clamp_min) / (clamp_max - clamp_min)

    if heat <= 3:  # Green -> Yellow
        ratio = normalized / 0.75
        r = int(0 + ratio * 255)  # Gradually increase red
        g = 255
        b = 0

    else:  # Yellow -> Red
        ratio = (normalized - 0.5) / 0.5
        r = 255
        g = int(255 - ratio * 255)  # Gradually decrease green
        b = 0

    return (r, g, b)


def ymd(epoch: Number):
    """Get YYYY-MM-DD formatted timestamp from an epoch value."""
    return get_date(epoch).strftime("%Y-%m-%d")


def hhmm(epoch: Number):
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


def get_lane_letter(part: dict):
    """Fetch the lane name from a "roompart" object as a modified single-letter variant."""
    name: str = part.get("roomPartName", "")

    return name.replace("Rata ", "").replace("pää", "")[:1]

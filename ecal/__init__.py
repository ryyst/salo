from .config import EcalConfig
from .fetch import fetch_events
from .render import render_events_html
from .transform import transform_events


EVENT_CALENDAR_REGISTRY = {
    "fetch": {
        "events": fetch_events,
    },
    "transform": {
        "events": transform_events,
    },
    "render": {
        "html_events": render_events_html,
    },
    "parser": {
        "base": EcalConfig,
    },
}

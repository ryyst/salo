from auki.config import AukiConfig
from auki.fetch import fetch_schedule, fetch_html, fetch_combined
from auki.render import render_schedule_html
from auki.transform import transform_combined, transform_library, transform_pharmacy


AUKI_REGISTRY = {
    "fetch": {
        "schedule": fetch_schedule,
        "html": fetch_html,
        "combined": fetch_combined,
    },
    "transform": {
        "combined": transform_combined,
        "library": transform_library,
        "pharmacy": transform_pharmacy,
    },
    "render": {
        "html_schedule": render_schedule_html,
    },
    "parser": {
        "base": AukiConfig,
    },
}

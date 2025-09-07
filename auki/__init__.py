from auki.config import AukiConfig
from auki.fetch import fetch_schedule
from auki.render import render_schedule_html
from auki.transform import transform_schedule


AUKI_REGISTRY = {
    "fetch": {
        "schedule": fetch_schedule,
    },
    "transform": {
        "schedule": transform_schedule,
    },
    "render": {
        "html_schedule": render_schedule_html,
    },
    "parser": {
        "base": AukiConfig,
    },
}

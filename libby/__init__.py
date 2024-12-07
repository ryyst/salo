from libby.config import LibbyConfig
from libby.fetch import fetch_schedule
from libby.render import render_schedule_html
from libby.transform import transform_schedule


LIBBY_REGISTRY = {
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
        "base": LibbyConfig,
    },
}

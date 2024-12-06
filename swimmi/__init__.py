from .transform import transform_single, transform_multi
from .fetch import fetch_single, offline_fetch_single, fetch_multi, offline_fetch_multi
from .render import render_html_multi, render_html_single, render_json_mocks
from .config import SwimmiConfig


SWIMMI_REGISTRY = {
    "fetch": {
        "single": fetch_single,
        "multi": fetch_multi,
        "offline_single": offline_fetch_single,
        "offline_multi": offline_fetch_multi,
    },
    "transform": {
        "single": transform_single,
        "multi": transform_multi,
    },
    "render": {
        "json_mocks": render_json_mocks,
        "html_multi": render_html_multi,
        "html_single": render_html_single,
    },
    "parser": {
        "base": SwimmiConfig,
    },
}

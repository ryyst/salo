from __future__ import annotations

from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from config import register_runner
from utils.renderers import render_html, save_file

from .config import ToriConfig
from .fetch import fetch_events
from .transform import transform_events

jinja = Environment(loader=FileSystemLoader("."), autoescape=select_autoescape())


def _render_events_html(data: Any, params: ToriConfig) -> None:
    """Render events HTML page"""
    html = render_html(data, params.render_template)
    filename = params.render_out_dir + "index.html"
    save_file(filename, html)


@register_runner("tori", ToriConfig, "Local event calendar")
def run_tori(params: ToriConfig) -> None:
    """Fetch, process and render event calendar"""

    # 1. Fetch raw event data
    raw_data = fetch_events(params)

    # 2. Transform events data
    transformed_data = transform_events(raw_data, params)

    # 3. Render events HTML page
    _render_events_html(transformed_data, params)

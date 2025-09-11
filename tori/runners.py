from __future__ import annotations
import os

from config import register_runner, get_output_dir
from utils.renderers import render_html, save_file

from .config import ToriConfig
from .fetch import fetch_events
from .transform import transform_events


@register_runner("tori", ToriConfig, "Local event calendar")
def run_tori(params: ToriConfig) -> None:
    """Fetch, process and render event calendar"""

    # 1. Fetch raw event data
    raw_data = fetch_events(params)

    # 2. Transform events data
    transformed_data = transform_events(raw_data, params)

    # 3. Render events HTML page
    template_path = "tori/template.html"  # Hardcoded template path
    html = render_html(transformed_data, template_path)

    # Use CLI output directory + runner name
    output_dir = os.path.join(get_output_dir(), "tori")
    filename = os.path.join(output_dir, "index.html")
    save_file(filename, html)

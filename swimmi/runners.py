from __future__ import annotations
import os

from config import register_runner, get_output_dir
from utils.renderers import render_html, save_file

from .config import SwimmiConfig
from .fetch import fetch_multi
from .transform import transform_multi
from .utils import get_epoch, ymd


@register_runner("swimmi", SwimmiConfig, "Human-readable swimming pool schedule")
def run_swimmi(params: SwimmiConfig) -> None:
    """Fetch, process and render swimming pool schedules for multiple days"""

    # 1. Fetch raw data
    raw_data = fetch_multi(params)

    # 2. Transform raw data
    transformed_data = transform_multi(raw_data, params)

    # 3. Render multi-day HTML pages
    template_path = "swimmi/template.html"  # Hardcoded template path

    # Use CLI output directory + runner name
    output_dir = os.path.join(get_output_dir(), "swimmi")

    for page in transformed_data:
        html = render_html(page, template_path)

        today_ymd = ymd(get_epoch())
        page_ymd = ymd(page.epoch)

        filename = "index" if page_ymd == today_ymd else page_ymd
        fullpath = os.path.join(output_dir, filename + ".html")

        save_file(fullpath, html)

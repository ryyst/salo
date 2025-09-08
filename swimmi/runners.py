from __future__ import annotations

from config import register_runner
from utils.renderers import render_html, save_file

from .config import SwimmiConfig
from .fetch import fetch_multi
from .transform import transform_multi
from .utils import get_epoch, ymd
from .schemas import RenderData


def _render_html_multi(pages: list[RenderData], params: SwimmiConfig) -> None:
    """Render multiple swimming pool schedule pages"""
    for page in pages:
        html = render_html(page, params.render_template)

        today_ymd = ymd(get_epoch())
        page_ymd = ymd(page.epoch)

        filename = "index" if page_ymd == today_ymd else page_ymd
        fullpath = params.render_out_dir + filename + ".html"

        save_file(fullpath, html)


@register_runner("swimmi", SwimmiConfig, "Human-readable swimming pool schedule")
def run_swimmi(params: SwimmiConfig) -> None:
    """Fetch, process and render swimming pool schedules for multiple days"""

    # 1. Fetch raw data
    raw_data = fetch_multi(params)

    # 2. Transform raw data
    transformed_data = transform_multi(raw_data, params)

    # 3. Render multi-day HTML pages
    _render_html_multi(transformed_data, params)

from __future__ import annotations
import os

from config import register_runner, get_output_dir
from utils.renderers import render_html, save_file

from .config import UuttaConfig
from .fetch import fetch_sss_rss, fetch_salo_rss
from .transform import transform_articles


@register_runner("uutta", UuttaConfig, "Local news aggregator")
def run_uutta(params: UuttaConfig) -> None:
    """Fetch, process and render local news articles"""

    # 1. Fetch raw RSS data from both sources
    sss_data = fetch_sss_rss(params)
    salo_data = fetch_salo_rss(params)

    # 2. Transform and combine articles from both sources
    transformed_data = transform_articles(sss_data.articles, salo_data.articles, params)

    # 3. Render news HTML page
    template_path = "uutta/templates/template.html"
    html = render_html(transformed_data, template_path)

    # Use CLI output directory + runner name
    output_dir = os.path.join(get_output_dir(), "uutta")
    filename = os.path.join(output_dir, params.output_file)
    save_file(filename, html)

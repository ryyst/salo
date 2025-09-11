from __future__ import annotations
import os

from config import register_runner, get_output_dir
from utils.renderers import render_html, save_file

from .config import AukiConfig
from .fetch import fetch_combined, fetch_library, fetch_pharmacy_ya
from .transform import transform_combined, transform_library, transform_pharmacy


@register_runner("auki", AukiConfig, "Opening hours aggregator for common services")
def run_auki(params: AukiConfig) -> None:
    """Process and render combined opening hours for libraries and pharmacies"""

    # 1. Fetch raw data
    raw_data = fetch_combined(params)

    # 2. Transform raw data
    transformed_data = transform_combined(raw_data, params)

    # 3. Render to HTML
    template_path = "auki/template.html"  # Hardcoded template path
    html = render_html(transformed_data, template_path)

    # Use CLI output directory + runner name
    output_dir = os.path.join(get_output_dir(), "auki")
    filename = os.path.join(output_dir, "index.html")
    save_file(filename, html)

import shutil
import os
from pathlib import Path
from config import register_runner, get_output_dir
from utils.renderers import render_html, save_file
from utils.logging import Log
from .config import KojeConfig


@register_runner("koje", KojeConfig, "Main dashboard container application")
def run_koje(params: KojeConfig):
    """Generate the main dashboard container application"""

    output_dir = os.path.join(get_output_dir(), "koje")
    filename = os.path.join(output_dir, "index.html")

    # Render the main HTML file
    data = {
        "iframes": [iframe.dict() for iframe in params.iframes],
        "title": params.title,
        "description": params.description,
    }

    html_content = render_html(data, "koje/template.html")
    save_file(filename, html_content)

    # Copy all static files
    static_dir = Path("koje/static")
    if static_dir.exists():
        for static_file in static_dir.iterdir():
            if static_file.is_file():
                Log.info(f"Copying static file: {static_file.name}")
                shutil.copy2(static_file, os.path.join(output_dir, static_file.name))

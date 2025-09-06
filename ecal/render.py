from typing import Any
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from utils.renderers import save_file
from .config import EcalConfig

jinja = Environment(loader=FileSystemLoader("."), autoescape=select_autoescape())


def render_events_html(data: Any, params: EcalConfig):
    template = jinja.get_template(params.render_template)
    rendered = template.render(data=data, page_header=params.page_header)
    filename = params.render_out_dir + "index.html"
    save_file(filename, rendered)

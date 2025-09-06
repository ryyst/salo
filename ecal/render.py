from typing import Any

from utils.renderers import render_html, save_file

from .config import EcalConfig


def render_events_html(data: Any, params: EcalConfig):

    data = render_html(data, params.render_template)
    filename = params.render_out_dir + "index.html"
    save_file(filename, data)

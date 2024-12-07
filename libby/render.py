from libby.config import LibbyConfig
from utils.renderers import render_html, save_file


def render_schedule_html(data, params: LibbyConfig):

    data = render_html(data, params.render_template)
    filename = params.render_out_dir + "index.html"
    save_file(filename, data)

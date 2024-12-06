from pydantic import BaseModel

from swimmi.config import SwimmiConfig
from swimmi.utils import get_epoch, ymd
from utils.renderers import render_html, save_file
from swimmi.schemas import RenderData


def render_html_single(page: RenderData, params: SwimmiConfig):
    data = render_html(page, params.render_template)
    filename = params.render_out_dir + "index.html"
    save_file(filename, data)


def render_html_multi(pages: list[RenderData], params: SwimmiConfig):
    for page in pages:
        data = render_html(page, params.render_template)

        today_ymd = ymd(get_epoch())
        page_ymd = ymd(page.epoch)

        filename = "index" if page_ymd == today_ymd else page_ymd
        fullpath = params.render_out_dir + filename + ".html"

        save_file(fullpath, data)


def render_json_mocks(files: list[BaseModel], _: SwimmiConfig):
    for i, file in enumerate(files):
        data = file.model_dump_json(indent=2)

        filename = "swimmi/mocks/" + str(i) + ".json"

        save_file(filename, data)

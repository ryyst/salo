from pydantic import BaseModel

from swimmi.config import SwimmiConfig
from utils.renderers import render_html, save_file
from swimmi.schemas import PageData, FileData


def render_html_single(page: PageData, params: SwimmiConfig):
    data = render_html(page, params.render_template)
    filename = params.render_out_dir + "index.html"
    save_file(filename, data)


def render_html_multi(files: list[FileData], params: SwimmiConfig):
    for file in files:
        data = render_html(file.data, params.render_template)

        filename = params.render_out_dir + file.name + ".html"

        save_file(filename, data)


def render_json_mocks(files: list[BaseModel], _: SwimmiConfig):
    for i, file in enumerate(files):
        data = file.model_dump_json(indent=2)

        filename = "swimmi/mocks/" + str(i) + ".json"

        save_file(filename, data)

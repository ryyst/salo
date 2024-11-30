from pydantic import BaseModel

from swimmi.config import RENDER_OUT_DIR, RENDER_TEMPLATE
from utils.renderers import render_html, save_file
from swimmi.transform import FileData, PageData


def render_html_single(page: PageData):
    data = render_html(page, RENDER_TEMPLATE)
    filename = RENDER_OUT_DIR + "index.html"
    save_file(filename, data)


def render_html_multi(files: list[FileData]):
    for file in files:
        data = render_html(file.data, RENDER_TEMPLATE)

        filename = RENDER_OUT_DIR + file.name + ".html"

        save_file(filename, data)


def render_json_mocks(files: list[BaseModel]):
    for i, file in enumerate(files):
        data = file.model_dump_json(indent=2)

        filename = "swimmi/mocks/" + str(i) + ".json"

        save_file(filename, data)

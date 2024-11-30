from utils.renderers import render_html, save_file

from swimmi.config import RENDER_OUT_DIR, RENDER_TEMPLATE
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

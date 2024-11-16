from utils.renderers import render_html, save_file

from swimmi.transform import FileData, PageData

# Paths from project root
template = "swimmi/template.html"
out_dir = "_out/swimmi/"


def render_html_single(page: PageData):
    data = render_html(page, template)
    filename = out_dir + "index.html"
    save_file(filename, data)


def render_html_multi(files: list[FileData]):
    for file in files:
        data = render_html(file.data, template)

        filename = out_dir + file.name + ".html"

        save_file(filename, data)

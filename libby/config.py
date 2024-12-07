from utils.schema import JSONModel


class LibbyConfig(JSONModel):
    library_id: str
    page_header: str
    render_out_dir: str
    render_template: str

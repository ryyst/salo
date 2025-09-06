from utils.schema import JSONModel


class ToriConfig(JSONModel):
    page_header: str
    render_out_dir: str
    render_template: str
    api_base_url: str

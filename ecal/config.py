from utils.schema import JSONModel


class EcalConfig(JSONModel):
    page_header: str
    render_out_dir: str
    render_template: str

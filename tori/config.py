from pydantic import Field
from utils.schema import JSONModel


class ToriConfig(JSONModel):
    page_header: str = Field(description="Title displayed on the generated page")
    render_out_dir: str = Field(description="Output directory for generated HTML")
    render_template: str = Field(description="Path to Jinja2 template file")
    api_base_url: str = Field(description="Base URL for the events API")

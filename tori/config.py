from pydantic import Field
from utils.schema import JSONModel


class ToriConfig(JSONModel):
    page_header: str = Field(description="Title displayed on the generated page")
    api_base_url: str = Field(description="Base URL for the events API")

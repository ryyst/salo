from pydantic import Field
from utils.schema import JSONModel


class AukiConfig(JSONModel):
    library_id: str = Field(description="Library ID for Kirjastot.fi API")
    location_id: str = Field(description="Location ID for HTML scrapers (pharmacy locations, etc.)")

    css_selector: str = Field(description="CSS selector for HTML scrapers")

    page_header: str = Field(description="Title displayed on the generated page")

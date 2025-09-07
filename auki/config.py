from utils.schema import JSONModel


class AukiConfig(JSONModel):
    # Data source identifiers (use one depending on the data source)
    library_id: str  # For Kirjastot.fi API
    location_id: str  # For HTML scrapers (pharmacy locations, etc.)

    # HTML scraping configuration
    css_selector: str  # CSS selector for HTML scrapers

    # Rendering configuration
    page_header: str
    render_out_dir: str
    render_template: str

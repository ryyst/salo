from utils.basescraper import BaseScraper
from utils.cache import cache_output

from .api import LibbyAPI
from .config import AukiConfig
from .schema import RawData, RawHTML, CombinedRawData


@cache_output("libby_raw", RawData)
def fetch_schedule(params: AukiConfig) -> RawData:
    api = LibbyAPI()

    response = api.get_open_hours(params.library_id)

    # TODO
    return RawData(data=response.data["data"])


@cache_output("html_raw", RawHTML)
def fetch_html(params: AukiConfig) -> RawHTML:
    api = BaseScraper("https://www.yliopistonapteekki.fi")

    extracted_text = api.get_html(params.location_id, params.css_selector)

    return RawHTML(data=extracted_text)


@cache_output("combined_raw", CombinedRawData)
def fetch_combined(params: AukiConfig) -> CombinedRawData:
    """Fetch both library and pharmacy data and return combined results"""
    library_data = None
    pharmacy_data = None

    # Fetch library data if library_id is provided
    if params.library_id:
        library_data = fetch_schedule(params)

    # Fetch pharmacy data if location_id and css_selector are provided
    if params.location_id and params.css_selector:
        pharmacy_data = fetch_html(params)

    return CombinedRawData(library=library_data, pharmacy=pharmacy_data)

from utils.basescraper import BaseScraper
from utils.cache import cache_output

from .api import LibbyAPI
from .config import AukiConfig
from .schema import LibraryData, RawData


@cache_output("library_raw", LibraryData)
def fetch_library(params: AukiConfig) -> LibraryData:
    api = LibbyAPI()

    response = api.get_open_hours(params.library_id)

    return LibraryData(**response.data["data"])


@cache_output("pharmacy_ya", str)
def fetch_pharmacy_ya(params: AukiConfig) -> str:
    api = BaseScraper("https://www.yliopistonapteekki.fi")

    extracted_text = api.get_html(params.location_id, params.css_selector)

    return extracted_text


@cache_output("auki_raw", RawData)
def fetch_combined(params: AukiConfig) -> RawData:
    """Fetch both library and pharmacy data and return combined results"""
    library_data = None
    pharmacy_data = None

    # Fetch library data if library_id is provided
    if params.library_id:
        library_data = fetch_library(params)

    # Fetch pharmacy data if location_id and css_selector are provided
    if params.location_id and params.css_selector:
        pharmacy_data = fetch_pharmacy_ya(params)

    return RawData(library=library_data, pharmacy=pharmacy_data)

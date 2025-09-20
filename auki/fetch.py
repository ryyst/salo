import json
import re
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


@cache_output("krauta_raw", dict)
def fetch_krauta(params: AukiConfig) -> dict:
    """Fetch K-Rauta opening hours from HTML table"""
    from bs4 import BeautifulSoup

    scraper = BaseScraper(params.krauta_url)
    response = scraper.request("GET", "", useJSON=False)

    if not response.ok:
        return {}

    soup = BeautifulSoup(response.data, "html.parser")

    # Find the opening hours table
    table = soup.select_one(".store-opening-times__table")
    if not table:
        return {}

    opening_hours = []
    for row in table.select("tbody tr"):
        cells = row.select("td")
        if len(cells) == 2:
            day_text = cells[0].get_text(strip=True)
            time_text = cells[1].get_text(strip=True)

            # Convert time format from "07 - 18" to "07-18" (no seconds)
            if " - " in time_text:
                start, end = time_text.split(" - ")
                formatted_time = f"{start.zfill(2)}-{end.zfill(2)}"
                opening_hours.append({"day": day_text, "hours": formatted_time})

    return {"opening_hours": opening_hours, "name": "K-Rauta Passeli"} if opening_hours else {}


@cache_output("auki_raw", RawData)
def fetch_combined(params: AukiConfig) -> RawData:
    """Fetch library, pharmacy and K-Rauta data and return combined results"""
    library_data = None
    pharmacy_data = None
    krauta_data = None

    # Fetch library data if library_id is provided
    if params.library_id:
        library_data = fetch_library(params)

    # Fetch pharmacy data if location_id and css_selector are provided
    if params.location_id and params.css_selector:
        pharmacy_data = fetch_pharmacy_ya(params)

    # Fetch K-Rauta data if krauta_url is provided
    if params.krauta_url:
        krauta_data = fetch_krauta(params)

    return RawData(library=library_data, pharmacy=pharmacy_data, krauta=krauta_data)

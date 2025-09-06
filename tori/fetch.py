from utils.cache import cache_output

from .api import EventCalendarAPI
from .config import ToriConfig
from .schema import RawData


@cache_output("tori_raw", RawData)
def fetch_events(params: ToriConfig) -> RawData:
    api = EventCalendarAPI(params.api_base_url)

    response = api.get_events()

    return RawData(events=response.data["posts"])

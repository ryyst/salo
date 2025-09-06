from utils.cache import cache_output

from .api import EventCalendarAPI
from .config import EcalConfig
from .schema import RawData


@cache_output("ecal_raw", RawData)
def fetch_events(_: EcalConfig) -> RawData:
    api = EventCalendarAPI()

    response = api.get_events()

    return RawData(events=response.data["posts"])

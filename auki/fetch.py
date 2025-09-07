from utils.cache import cache_output

from .api import LibbyAPI
from .config import AukiConfig
from .schema import RawData


@cache_output("libby_raw", RawData)
def fetch_schedule(params: AukiConfig) -> RawData:
    api = LibbyAPI()

    response = api.get_open_hours(params.library_id)

    # TODO
    return RawData(data=response.data["data"])

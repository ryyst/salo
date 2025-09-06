from utils.cache import cache_output

from .api import LibbyAPI
from .config import LibbyConfig
from .schema import RawData


@cache_output("libby_raw", RawData)
def fetch_schedule(params: LibbyConfig) -> RawData:
    api = LibbyAPI()

    response = api.get_open_hours(params.library_id)

    # TODO
    return RawData(data=response.data["data"])

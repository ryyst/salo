from libby.api import LibbyAPI
from libby.config import LibbyConfig
from libby.schema import RawData
from utils.cache import cache_output


@cache_output("libby_raw", RawData)
def fetch_schedule(params: LibbyConfig) -> RawData:
    api = LibbyAPI()

    response = api.get_open_hours(params.library_id)

    # TODO
    return RawData(data=response.data["data"])

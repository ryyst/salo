from utils.cache import cache_output

from .api import AukiAPI
from .config import AukiConfig
from .schema import RawData


@cache_output("auki_raw", RawData)
def fetch_schedule(params: AukiConfig) -> RawData:
    api = AukiAPI()

    response = api.get_open_hours(params.library_id)

    # TODO
    return RawData(data=response.data["data"])

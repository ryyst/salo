from .config import LibbyConfig
from .schema import RawData


def transform_schedule(data: RawData, params: LibbyConfig):
    # TODO
    return data.data["schedules"]

from .config import AukiConfig
from .schema import RawData


def transform_schedule(data: RawData, params: AukiConfig):
    # TODO
    return data.data["schedules"]

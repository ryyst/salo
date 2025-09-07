from .config import AukiConfig
from .schema import RawData


def transform_schedule(data: RawData, params: AukiConfig):
    return data.data.schedules

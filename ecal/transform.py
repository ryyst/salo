import json

from .schema import RawData
from .config import EcalConfig


def transform_events(data: RawData, params: EcalConfig):

    return [json.dumps(e) for e in data.events]

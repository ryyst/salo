from pydantic import BaseModel


class RawData(BaseModel):
    """Contains all raw data fetched from tapahtumat.salo.fi"""

    events: list[dict]

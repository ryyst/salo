from pydantic import BaseModel


class RawData(BaseModel):
    """Contains all raw data fetched from Kirjastot.fi"""

    data: dict

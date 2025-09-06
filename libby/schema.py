from pydantic import BaseModel


class RawData(BaseModel):
    """Contains all raw data fetched from Kirjastot.fi"""

    # TODO: friggin data, for real now
    data: dict

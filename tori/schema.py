from pydantic import BaseModel


class RawData(BaseModel):
    """Contains all raw event data fetched from API."""

    events: list[dict]

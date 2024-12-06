from pydantic import BaseModel


#
# INPUT
#


class RawTimmiData(BaseModel):
    """Contains all Timmi data for a single page render."""

    epoch: int
    room_parts: list[dict]
    episodes: list[dict]


class RawData(BaseModel):
    """Contains all raw data fetched by Swimmi."""

    pages: list[RawTimmiData]


#
# OUTPUT
#


class RenderData(BaseModel):
    """Represents the transformed data we pass on to template."""

    epoch: int

    pools: list[dict]  # lazy typing

    hours: list[int]
    open_hours: list
    hours_heatmap: dict
    current_day_stamp: str
    updated_stamp: str
    prev_date_link: str
    next_date_link: str
    is_today: bool
    page_header: str

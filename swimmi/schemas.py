from typing import Optional
from pydantic import BaseModel

from utils.schema import JSONModel


class ExtraOpenHours(JSONModel):
    """Baserow database row type for extra open hours info."""

    id: int
    order: str
    date: str
    open_from: Optional[int] = None
    open_to: Optional[int] = None
    note: Optional[str] = None
    created: str


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
    extra_open_hours: list[ExtraOpenHours]


#
# OUTPUT
#


class RenderData(BaseModel):
    """Represents the transformed data we pass on to template."""

    epoch: int

    pools: list[dict]  # lazy typing

    hours: list[int]
    open_hours: list
    is_closed: bool
    hours_note: str
    hours_heatmap: dict
    current_day_stamp: str
    updated_timestamp: str
    prev_date_link: str
    next_date_link: str
    is_today: bool
    page_header: str

from pydantic import BaseModel


#
# INPUT
#


class RawPageData(BaseModel):
    """Represents the data format we pass on directly from API response."""

    room_parts: list[dict]
    episodes: list[dict]


class RawDayData(BaseModel):
    """Maps page data to the epoch stamp used in fetching."""

    page: RawPageData
    epoch: int


#
# OUTPUT
#


class PageConfig(BaseModel):
    hours: list
    open_hours: list
    hours_heatmap: dict
    current_day_stamp: str
    updated_stamp: str
    prev_date_link: str
    next_date_link: str
    is_today: bool
    page_header: str


class PageData(BaseModel):
    """Represents the transformed data we pass on to template."""

    pools: list[dict]  # lazy typing
    config: PageConfig


class FileData(BaseModel):
    """Represents the transformed data we pass on to template."""

    data: PageData
    name: str

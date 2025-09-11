from typing import Optional
from pydantic import Field
from utils.schema import JSONModel


class BaserowConfig(JSONModel):
    db_token: str = Field(description="Database token for baserow.io")
    table_id: str = Field(description="Table ID in baserow.io")


class MarkerConfig(JSONModel):
    whole_pool_lanes: list[str] = Field(description="Lane names for whole pool bookings")
    half_pool_lanes: list[str] = Field(description="Lane names for half pool bookings")
    single_lane_pools: list[str] = Field(description="Pool names for single lane bookings")


class SwimmiConfig(JSONModel):
    host: str = Field(description="Base URL for the swimming pool booking system")

    login_params: dict = Field(description="GET parameters for authentication")
    room_parts_params: dict = Field(description="GET parameters for room selection")

    future_days_count: int = Field(description="Number of future days to fetch")
    past_days_count: int = Field(description="Number of past days to fetch")

    page_header: str = Field(description="Title displayed on the generated page")
    render_hours: tuple[int, int] = Field(description="Start and end hours for rendering")

    open_hours: list[tuple[int, int]] = Field(
        description="Daily opening hours [start, end] for each weekday"
    )
    special_markers: MarkerConfig = Field(description="Configuration for special lane/pool markers")

    baserow: Optional[BaserowConfig] = Field(
        default=None,
        description="Optional baserow.io integration for additional hours data",
    )

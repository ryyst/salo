from typing import Optional
from utils.schema import JSONModel


class BaserowConfig(JSONModel):
    db_token: str
    table_id: str


class MarkerConfig(JSONModel):
    whole_pool_lanes: list[str]
    half_pool_lanes: list[str]
    single_lane_pools: list[str]


class SwimmiConfig(JSONModel):
    host: str

    login_params: dict
    """Unvalidated collection of GET parameters, varies by env."""

    room_parts_params: dict
    """Unvalidated collection of GET parameters, varies by env."""

    future_days_count: int
    past_days_count: int

    page_header: str
    render_hours: tuple[int, int]
    render_out_dir: str
    render_template: str

    open_hours: list[tuple[int, int]]
    special_markers: MarkerConfig

    baserow: Optional[BaserowConfig] = None
    """Additional hour data is kept in baserow.io."""

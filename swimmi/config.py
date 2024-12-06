from utils.schema import JSONModel


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

    page_header: str
    render_hours: tuple[int, int]
    render_out_dir: str
    render_template: str

    open_hours: list[tuple[int, int]]
    special_markers: MarkerConfig

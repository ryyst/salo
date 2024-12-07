from api.baserow import BaserowAPI
from swimmi.config import SwimmiConfig
from swimmi.api import SwimmiAPI
from utils.cache import cache_output
from utils.logging import Log
from swimmi.utils import get_epoch

from swimmi.schemas import ExtraOpenHours, RawTimmiData, RawData


def _fetch_extra_hours(params: SwimmiConfig) -> list[ExtraOpenHours]:
    try:
        baserow = params.baserow
        if baserow:
            api = BaserowAPI(baserow.db_token)
            data = api.get_table_rows(baserow.table_id)

            rows = [ExtraOpenHours(**r) for r in data.results]
            return rows
    except Exception as err:
        Log.warning("Tried to get extra hours data but failed: %s", err)
        pass

    return []


@cache_output("swimmi_raw", RawData)
def fetch_multi(params: SwimmiConfig) -> RawData:
    """Fetch all relevant data from Timmi for multiple days."""
    api = SwimmiAPI(params.host, params.login_params, params.room_parts_params)

    def fetch_day():
        room_parts, episodes = api.get_day_schedule()
        return RawTimmiData(room_parts=room_parts, episodes=episodes, epoch=get_epoch())

    def fetch_next_date(delta: int):
        delta_resp = api.change_day_delta(delta)
        new_day = fetch_day()
        # Fix epoch for non-today dates
        new_day.epoch = delta_resp.data.get("newDate", 0)

        return new_day

    today = fetch_day()

    future = []
    past = []

    past_count = params.past_days_count
    future_count = params.past_days_count

    # Future N days
    for _ in range(future_count):
        future.append(fetch_next_date(+1))

    # If we want any past days we'll first reset backend back to `today`, mostly for easier iteration.
    if past_count > 0 and future_count > 0:
        api.change_day_delta(-future_count)

    # Past N days
    for _ in range(past_count):
        past.append(fetch_next_date(-1))

    return RawData(
        pages=[*past, today, *future],
        extra_open_hours=_fetch_extra_hours(params),
    )

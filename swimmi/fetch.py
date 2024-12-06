import json

from swimmi.config import SwimmiConfig
from swimmi.api import SwimmiAPI
from utils.logging import Log
from swimmi.utils import get_epoch

from swimmi.schemas import RawTimmiData, RawData


def offline_fetch_multi(params: SwimmiConfig) -> list[RawData]:
    """Mock Timmi data from offline backup."""
    days = []

    Log.info("Using offline data dumps.")

    for n in range(1, 10):
        with open(f"swimmi/mocks/{n}.json", "rb") as file:
            day = json.loads(file.read())
            days.append(RawData(**day))

    return days


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

    # Future N days
    future = []
    future_count = 7
    for _ in range(future_count):
        future.append(fetch_next_date(+1))

    # Back to today
    api.change_day_delta(-future_count)

    # Past N days
    past = []
    past_count = 2
    for _ in range(past_count):
        past.append(fetch_next_date(-1))

    return RawData(
        pages=[*past, today, *future],
    )

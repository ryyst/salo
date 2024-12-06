import json

from swimmi.config import SwimmiConfig
from swimmi.api import SwimmiAPI
from utils.logging import Log
from swimmi.utils import get_epoch

from swimmi.schemas import RawPageData, RawDayData


def offline_fetch_single(_: SwimmiConfig) -> RawPageData:
    """Mock Timmi data from offline backup."""
    episodes = []
    room_parts = []

    Log.info("Using offline data dumps.")

    with open("swimmi/mocks/episodes.json", "rb") as file:
        episodes = json.loads(file.read())

    with open("swimmi/mocks/roomparts.json", "rb") as file:
        room_parts = json.loads(file.read())

    return RawPageData(room_parts=room_parts, episodes=episodes)


def offline_fetch_multi(_: SwimmiConfig) -> list[RawDayData]:
    """Mock Timmi data from offline backup."""
    days = []

    Log.info("Using offline data dumps.")

    for n in range(1, 10):
        with open(f"swimmi/mocks/{n}.json", "rb") as file:
            day = json.loads(file.read())
            days.append(RawDayData(**day))

    return days


def fetch_single(params: SwimmiConfig) -> RawPageData:
    """Fetch all relevant data from Timmi for a single day."""

    api = SwimmiAPI(params.host, params.login_params, params.room_parts_params)

    room_parts, episodes = api.get_day_schedule(get_epoch())

    return RawPageData(room_parts=room_parts, episodes=episodes)


def fetch_multi(params: SwimmiConfig) -> list[RawDayData]:
    """Fetch all relevant data from Timmi for multiple days."""
    now = get_epoch()

    api = SwimmiAPI(params.host, params.login_params, params.room_parts_params)

    def fetch_day():
        room_parts, episodes = api.get_day_schedule(now)
        return RawPageData(room_parts=room_parts, episodes=episodes)

    today = RawDayData(page=fetch_day(), epoch=now)

    # Future N days
    future = []
    day_count = 7
    for _ in range(day_count):
        delta_resp = api.change_day_delta(+1, now)
        new_day = RawDayData(page=fetch_day(), epoch=delta_resp.data.get("newDate", 0))
        future.append(new_day)

    # Yesterday
    days_since_yesterday = day_count + 1
    delta_resp = api.change_day_delta(-days_since_yesterday, now)
    yesterday = RawDayData(page=fetch_day(), epoch=delta_resp.data.get("newDate", 0))

    # The Day Before:
    # Yesterday's "next day" link is always to /, which is not nice in history.
    # Lazy solution: fetch one extra past day so that we start cumulating valid history.
    delta_resp = api.change_day_delta(-1, now)
    tdb = RawDayData(page=fetch_day(), epoch=delta_resp.data.get("newDate", 0))

    return [tdb, yesterday, today, *future]

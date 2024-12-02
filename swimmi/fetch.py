import json

from swimmi.api import SwimmiAPI
from utils.logging import Log
from swimmi.utils import get_epoch

from swimmi.schemas import RawPageData, RawDayData


api = SwimmiAPI()


def offline_fetch_single() -> RawPageData:
    """Mock Timmi data from offline backup."""
    episodes = []
    room_parts = []

    Log.info("Using offline data dumps.")

    with open("swimmi/mocks/episodes.json", "rb") as file:
        episodes = json.loads(file.read())

    with open("swimmi/mocks/roomparts.json", "rb") as file:
        room_parts = json.loads(file.read())

    return RawPageData(room_parts=room_parts, episodes=episodes)


def offline_fetch_multi() -> list[RawDayData]:
    """Mock Timmi data from offline backup."""
    days = []

    Log.info("Using offline data dumps.")

    for n in range(1, 10):
        with open(f"swimmi/mocks/{n}.json", "rb") as file:
            day = json.loads(file.read())
            days.append(RawDayData(**day))

    return days


def fetch_single() -> RawPageData:
    """Fetch all relevant data from Timmi for a single day."""

    # Fetch room parts. Note that this sets the backend session to fetch all
    # episodes for given rooms in the next step.
    response = api.get_room_parts(get_epoch())
    if not response:
        print("No data received! Aborting...")
        raise Exception("No room data received.")

    room_parts = response.data if response.ok else []

    # Fetch episodes and add events to rooms
    response2 = api.get_episodes(get_epoch())
    episodes = response2.data if response2.ok else []

    return RawPageData(room_parts=room_parts, episodes=episodes)


def fetch_multi() -> list[RawDayData]:
    now = get_epoch()

    today = RawDayData(page=fetch_single(), epoch=now)

    # Future N days
    future = []
    day_count = 7
    for _ in range(day_count):
        delta_resp = api.change_day_delta(+1, now)
        new_day = RawDayData(
            page=fetch_single(), epoch=delta_resp.data.get("newDate", 0)
        )
        future.append(new_day)

    # Yesterday
    days_since_yesterday = day_count + 1
    delta_resp = api.change_day_delta(-days_since_yesterday, now)
    yesterday = RawDayData(page=fetch_single(), epoch=delta_resp.data.get("newDate", 0))

    # The Day Before:
    # Yesterday's "next day" link is always to /, which is not nice in history.
    # Lazy solution: fetch one extra past day so that we start cumulating valid history.
    delta_resp = api.change_day_delta(-1, now)
    tdb = RawDayData(page=fetch_single(), epoch=delta_resp.data.get("newDate", 0))

    return [tdb, yesterday, today, *future]

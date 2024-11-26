import locale
from dataclasses import dataclass
from datetime import datetime, timedelta

from swimmi.fetch import RawPageData, RawDayData
from swimmi.utils import (
    get_date,
    color_normalize,
    color_darken,
    get_epoch,
    ymd,
    hhmm,
    get_event_name,
    get_lane_letter,
)

# Set for easier time strings localisation.
locale.setlocale(locale.LC_TIME, "fi_FI.utf8")

# Hard-coded open hours of the hall from:
# https://salo.fi/vapaa-aika-ja-matkailu/liikunta/sisaliikuntapaikat/uimahalli/
#
# TODO: Needs some automagicks here.
OPEN_HOURS = [
    (6, 21),
    (6, 21),
    (12, 20),
    (6, 21),
    (6, 21),
    (11, 18),
    (11, 18),
]

# H = "Hyppyallas"
# K = "Kilpa-allas"
#
# Special lanes which actually mark the entire pools as reserved, instead of just one lane.
WHOLE_POOL_MARKER = ["H", "K"]

# M = "Matala pää"
# S = "Syvä pää"
#
# Special lanes which actually mark all other lanes *except* the other "pää" as reserved
HALF_POOL_MARKERS = ["M", "S"]

# T = "Terapia-allas"
# L = "Lasten allas"
#
# Pools which don't actually have any designated lanes.
SINGLE_LANE_POOLS = ["T", "L"]


@dataclass
class PageConfig:
    hours: list
    lanes: int
    current_day_stamp: str
    updated_stamp: str
    open_hours: list
    prev_date_link: str
    next_date_link: str
    is_today: bool


@dataclass
class PageData:
    """Represents the transformed data we pass on to template."""

    pools: list[dict]  # lazy typing
    config: PageConfig


@dataclass
class FileData:
    """Represents the transformed data we pass on to template."""

    data: PageData
    name: str


def _transform_page_data(data: RawPageData, page_date: datetime) -> PageData:
    """Transform all Timmi data into our own format for rendering."""
    pool_map = {}

    #
    # Step 1: Build the pool-lane hierarchy from flat Timmi data.
    #
    for part in data.room_parts:
        pool_id = part.get("roomId")
        lane_letter = get_lane_letter(part)

        # Don't add the special lanes themselves.
        if lane_letter in WHOLE_POOL_MARKER:
            continue

        rawname = part.get("roomName", "")

        # Fix egregious grammatic error in data
        name = "Hyppyallas" if rawname == "Hyppy-allas" else rawname

        if not pool_map.get(pool_id):
            # Pool not yet in mapping, add configuration.
            pool_map[pool_id] = {
                "room_id": pool_id,
                "name": name,
                "shortName": name[:4] + ".",
                "letter": name[:1],
                "info": part.get("additionalInfo"),
                "events": [],
                "lanes": [lane_letter],
            }
        else:
            # Pool already configured, just add a new lane.
            pool_map[pool_id]["lanes"].append(lane_letter)

    #
    # Step 2: Pre-process event data: filter out extras & sort by time.
    #
    def event_filter(ep: dict):
        """Filter out uninteresting events made by the swimming hall itself."""
        name = get_event_name(ep).lower()
        return (
            len(ep.get("eventTextField", []))
            and "ei varaus" not in name
            and "suljettu" not in name
        )

    filtered_events = [ep for ep in data.episodes if event_filter(ep)]

    sorted_events = sorted(
        filtered_events,
        key=lambda e: (e.get("startTime", {}).get("time", 0), get_lane_letter(e)),
    )

    #
    # Step 3: Attach each event to the relevant pool by id, easy while it's still a dict.
    #
    for e in sorted_events:
        pool_id = e.get("roomId")
        if pool_id not in pool_map:
            continue

        pool = pool_map[pool_id]

        start = e.get("startTime", {})
        end = e.get("endTime", {})

        lane = get_lane_letter(e)

        # Get rid of the jarring color/contrast differences that the API gives us
        color = color_normalize(
            (
                e.get("eventColorRed", 0),
                e.get("eventColorGreen", 0),
                e.get("eventColorBlue", 0),
            )
        )

        border_color = color_darken(color)

        event = {
            "usageRestriction": bool(e.get("usageRestrictionId")),
            "info": get_event_name(e),
            "lane": lane,
            "laneFull": e.get("roomPartName") if lane not in SINGLE_LANE_POOLS else "",
            "startHour": start.get("hours"),
            "startMin": start.get("minutes"),
            "endHour": end.get("hours"),
            "endMin": end.get("minutes"),
            # Lazy maths: ensure we really get every single hour that the event is "part of".
            "hours": list(
                set(
                    [
                        start.get("hours"),
                        *range(start.get("hours"), end.get("hours")),
                        end.get("hours") if end.get("minutes") != 0 else None,
                    ]
                )
            ),
            "color": (*color, 0.7),
            "borderColor": (*border_color, 0.7),
            "humanTime": f"{hhmm(start.get('time'))} - {hhmm(end.get('time'))}",
            "fake": False,
        }

        # Add a single fake event to every lane of the pool when we find one of
        # the "whole pool is actually reserved" lanes.
        if lane in WHOLE_POOL_MARKER:
            for l in pool["lanes"]:
                fake_event = event.copy()
                fake_event["lane"] = l
                fake_event["fake"] = True
                pool["events"].append(fake_event)

        # Add a single fake event to every *regular* lane of the pool when we find
        # one of the "half the pool is actually reserved" lanes.
        if lane in HALF_POOL_MARKERS:
            for l in pool["lanes"]:
                if l not in HALF_POOL_MARKERS:
                    fake_event = event.copy()
                    fake_event["lane"] = l
                    fake_event["fake"] = True
                    pool["events"].append(fake_event)

        pool["events"].append(event)

    #
    # Step 4: Turn hierarchial mapping into an easier flat list of pools instead.
    #
    pools = list(pool_map.values())

    #
    # Step 5: Pre-calculate navigation links
    #
    # Notice the critical distinction between "today" <-> "page_date" and "yesterday" <-> "prev_date".
    today = datetime.today()

    prev_date = page_date - timedelta(1)
    next_date = page_date + timedelta(1)

    is_today = page_date.date() == today.date()
    is_yesterday = (today - timedelta(1)).date() == page_date.date()
    is_tomorrow = (today + timedelta(1)).date() == page_date.date()

    #
    # Step 6: Configure some general attributes for the page.
    #
    config = PageConfig(
        hours=list(range(5, 23)),
        lanes=sum([len(r.get("lanes")) for r in pools]),
        current_day_stamp=page_date.strftime("%A %d.%m.").capitalize(),
        updated_stamp=today.strftime("%d.%m.%Y klo %H:%M"),
        open_hours=list(range(*OPEN_HOURS[page_date.weekday()])),
        # Pre-calculated links for rendering the navigation around current day
        prev_date_link="/" if is_tomorrow else "/" + prev_date.strftime("%Y-%m-%d"),
        next_date_link="/" if is_yesterday else "/" + next_date.strftime("%Y-%m-%d"),
        is_today=is_today,
    )

    return PageData(pools, config)


def transform_single(data: RawPageData) -> PageData:
    """Transform a single page, mostly for debugging purposes."""
    return _transform_page_data(data, datetime.today())


def transform_multi(data: list[RawDayData]) -> list[FileData]:
    """Transform all given pages."""
    today_ymd = ymd(get_epoch())

    days: list[FileData] = []
    for day in data:
        page_date = get_date(day.epoch)
        page = _transform_page_data(day.page, page_date)

        page_ymd = ymd(day.epoch)

        filename = "index" if page_ymd == today_ymd else page_ymd

        days.append(FileData(page, filename))

    return days

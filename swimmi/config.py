#
# General hard-coded parameters for rendering the swimmi data.
#

TIMMI = {
    # Note: public credentials
    "host": "https://tilavaraus.jict.fi/WebTimmi/",
    "login_params": {
        "loginName": "guest_kempele",
        "password": "salasana",
        "profileId": 547,
        "adminAreaId": 10,
    },
    "room_parts_params": {
        "type": 4,
        "ids": 547,
    },
}

PAGE_HEADER = "Zimmari"

RENDER_HOURS = list(range(5, 23))


# Hard-coded open hours of the hall from:
# https://salo.fi/vapaa-aika-ja-matkailu/liikunta/sisaliikuntapaikat/uimahalli/
#
# TODO: Needs some automagicks here.
OPEN_HOURS = [
    (12, 20),
    (6, 21),
    (6, 21),
    (6, 21),
    (9, 20),
    (9, 17),
    (9, 17),
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


# Paths from project root
RENDER_TEMPLATE = "swimmi/template.html"
RENDER_OUT_DIR = "_out/swimmi/"

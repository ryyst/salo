#
# General hard-coded parameters for rendering the swimmi data.
#

TIMMI = {
    # Note: public credentials
    "host": "https://asp3.timmi.fi/WebTimmi/",
    "login_params": {
        "loginName": "SALO_LIIKUNTA",
        "password": "GUEST",
        "roomId": 504480,
        "adminAreaId": 316,
    },
    "room_parts_params": {
        "type": 6,
        "ids": 1227,
    },
}

PAGE_HEADER = "Salon uimahalli"

RENDER_HOURS = list(range(5, 23))


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


# Paths from project root
RENDER_TEMPLATE = "swimmi/template.html"
RENDER_OUT_DIR = "_out/swimmi/"

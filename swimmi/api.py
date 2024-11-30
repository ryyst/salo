from swimmi.config import TIMMI
from utils.baseapi import BaseAPI


class SwimmiAPI(BaseAPI):
    """Timmi API client."""

    def __init__(self):
        super().__init__(TIMMI["host"])

    def login(self):
        self.request(
            "GET",
            "login.do",
            {"params": TIMMI["login_params"]},
            useJSON=False,
        )

    def _request(self, endpoint: str, config: dict):
        """Thin wrapper for parent `request()`:

        Ensure all Swimmi requests are always logged in.
        """
        if not self._session.cookies:
            self.login()

        return self.request("GET", endpoint, config)

    def change_day_delta(self, delta: int, epoch: int):
        """Move from current day either forward or backwards.

        The "current day" state is stored in Timmi's backend according to client's session ID.
        """
        return self._request(
            "calendarAjax.do",
            {
                "params": {
                    "actionCode": "changeDay",
                    "numberOfDaysToMove": delta,
                    "_": epoch,
                }
            },
        )

    def get_episodes(self, epoch: int):
        """Episodes AKA lane events."""
        return self._request(
            "calendarAjax.do",
            {"params": {"actionCode": "getEpisodes", "_": epoch}},
        )

    def get_room_parts(self, epoch: int):
        """Room parts AKA pool lanes."""
        return self._request(
            "getRoomPartsForCalendarAjax.do",
            {
                "params": {
                    "actionCode": "getRoomPartInfos",
                    **TIMMI["room_parts_params"],
                    "interpreterLangId": 0,
                    "cumulativeMode": 1,
                    "_": epoch,
                }
            },
        )

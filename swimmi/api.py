from utils.baseapi import BaseAPI
from utils.logging import Log

from swimmi.utils import get_epoch


class SwimmiAPI(BaseAPI):
    """Timmi API client."""

    def __init__(self, host: str, login_params: dict, room_parts_params: dict):
        super().__init__(host)
        self.login_params = login_params
        self.room_parts_params = room_parts_params

    def login(self):
        """Fetch our login token and instantiate the backend session, which is tied to this token."""
        self.request(
            "GET",
            "login.do",
            {"params": self.login_params},
            useJSON=False,
        )

    def _request(self, endpoint: str, config: dict):
        """Thin wrapper for parent `request()`:

        Ensure all Swimmi requests are always logged in.
        """
        if not self._session.cookies:
            self.login()

        return self.request("GET", endpoint, config)

    def change_day_delta(self, delta: int):
        """Move from current day either forward or backwards.

        The "current day" state is stored in Timmi's backend according to client's session ID.
        """
        return self._request(
            "calendarAjax.do",
            {
                "params": {
                    "actionCode": "changeDay",
                    "numberOfDaysToMove": delta,
                    "_": get_epoch(),
                }
            },
        )

    def get_episodes(self):
        """Episodes AKA lane events."""
        return self._request(
            "calendarAjax.do",
            {"params": {"actionCode": "getEpisodes", "_": get_epoch()}},
        )

    def get_room_parts(self):
        """Room parts AKA pool lanes."""
        return self._request(
            "getRoomPartsForCalendarAjax.do",
            {
                "params": {
                    "actionCode": "getRoomPartInfos",
                    **self.room_parts_params,
                    "interpreterLangId": 0,
                    "cumulativeMode": 1,
                    "_": get_epoch(),
                }
            },
        )

    def get_day_schedule(self):
        """Combined helper for getting all relevant schedule data for a single day."""

        # Note that this sets the backend session to fetch all episodes for given
        # list of rooms in the next step.
        response = self.get_room_parts()
        if not response:
            Log.warning("No room data received! Aborting...")
            raise Exception("No room data received.")

        room_parts = response.data if response.ok else []

        # Fetch episodes and add events to rooms
        response2 = self.get_episodes()
        episodes = response2.data if response2.ok else []

        return room_parts, episodes

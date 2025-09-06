from utils.baseapi import BaseAPI


class EventCalendarAPI(BaseAPI):
    """API client for tapahtumat.salo.fi data."""

    def __init__(self):
        super().__init__("https://tapahtumat.salo.fi/wp-json/everblox/v1")

    def get_events(self):
        return self.request(
            "GET",
            f"/eventcalendar",
            {
                "params": {
                    "lang": "fi",
                }
            },
        )

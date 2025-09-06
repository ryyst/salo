from utils.baseapi import BaseAPI


class EventCalendarAPI(BaseAPI):
    """API client for tapahtumat.salo.fi data."""

    def __init__(self, base_url: str):
        super().__init__(base_url)

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

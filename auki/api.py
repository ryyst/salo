from utils.baseapi import BaseAPI


class LibbyAPI(BaseAPI):
    """Kirjastot.fi API client."""

    def __init__(self):
        super().__init__("https://api.kirjastot.fi/v4")

    def get_open_hours(self, library_id: str):
        return self.request(
            "GET",
            f"/library/{library_id}",
            {
                "params": {
                    "lang": "fi",
                    "with": "schedules",
                    "refs": "period",
                    "period.start": "0w",
                    "period.end": "2w",
                }
            },
        )

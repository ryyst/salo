import urllib.parse
from typing import Any, Union

from pydantic import BaseModel
import requests

from utils.logging import Log


class ApiResponse(BaseModel):
    data: Any
    status: int
    ok: bool


class BaseAPI:
    """Simple HTTP API wrapper."""

    def __init__(self, base_url: str, headers: Union[dict, None] = None):
        self._session = requests.Session()
        self._session.headers.update({"Content-Type": "application/json"})

        if headers:
            self._session.headers.update(headers)

        self.base_url = base_url

    def request(
        self, method: str, endpoint: str, config: Union[dict, None] = None, useJSON=True
    ) -> ApiResponse:
        if config is None:
            config = {}

        url = f"{self.base_url}{endpoint}"
        qs = urllib.parse.urlencode(config.get("params", {}))

        try:
            response = self._session.request(method, url, **config)
            Log.debug("[%s] %s%s", response.status_code, url, qs)

            data = response.json() if useJSON else response.text

            return ApiResponse(
                data=data,
                status=response.status_code,
                ok=200 <= response.status_code < 400,
            )
        except Exception as error:
            Log.error("[%s] %s%s", 500, url, qs)
            Log.error("Error: %s", error)
            return ApiResponse(data=str(error), status=500, ok=False)

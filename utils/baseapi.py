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

    def __init__(self, base_url: str):
        self._session = requests.Session()
        self._session.headers.update({"Content-Type": "application/json"})

        self.base_url = base_url

    def request(
        self, method: str, endpoint: str, config: Union[dict, None] = None, useJSON=True
    ) -> ApiResponse:
        if config is None:
            config = {}

        url = f"{self.base_url}{endpoint}"
        qs = urllib.parse.urlencode(config.get("params", {}))

        Log.info("Calling url: %s%s", url, qs)

        try:
            response = self._session.request(method, url, **config)
            Log.info("Response status: %s", response.status_code)

            data = response.json() if useJSON else response.text

            return ApiResponse(
                data=data,
                status=response.status_code,
                ok=200 <= response.status_code < 400,
            )
        except Exception as error:
            Log.error("Error calling url: %s, %s", url, error)
            return ApiResponse(data=str(error), status=500, ok=False)

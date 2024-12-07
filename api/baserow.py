from typing import Any

from utils.baseapi import BaseAPI
from pydantic import BaseModel


class TableRows(BaseModel):
    count: int
    next: Any
    previous: Any
    results: list[dict]


class BaserowAPI(BaseAPI):
    """Baserow API client."""

    def __init__(self, token):
        super().__init__(
            "https://api.baserow.io/api", {"Authorization": f"Token {token}"}
        )

    def get_table_rows(self, table_id: str):
        response = self.request(
            "GET",
            f"/database/rows/table/{table_id}/",
            {"params": {"user_field_names": True}},
        )

        return TableRows(**response.data)

from pydantic import BaseModel
from typing import List, Dict, Any


class RawRSSData(BaseModel):
    """Contains raw RSS feed data."""

    articles: List[Dict[str, Any]]

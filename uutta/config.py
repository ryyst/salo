from typing import Optional
from utils.schema import JSONModel


class UuttaConfig(JSONModel):
    """Configuration for uutta (news aggregator) module."""

    # RSS feed URLs
    sss_rss_url: str = "https://www.sss.fi/feed/"
    salo_rss_url: str = "https://tiedotteet.salo.fi/feed/"

    # Output settings
    output_file: str = "index.html"
    template_name: str = "template.html"

    # Content filtering
    excluded_categories: list[str] = ["uutiset", "Uutiset", "Ulkomaat"]
    max_articles: Optional[int] = 20

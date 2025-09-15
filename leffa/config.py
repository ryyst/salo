from typing import List, Optional
from utils.schema import JSONModel


class TheaterConfig(JSONModel):
    name: str
    site_url: str  # For movie links and footer links
    api_url: str  # For API calls and image URLs
    movie_path: str = "elokuva"  # Movie page path (e.g. "elokuva" or "elokuva-2")
    location_id: int
    content_type_id: int = 1
    language: str = "fi"
    upcoming_only: bool = True
    # Allow theater-specific overrides for parameters


class LeffaConfig(JSONModel):
    theaters: List[TheaterConfig]
    days_ahead: int = 14
    output_dir: str = "leffa"

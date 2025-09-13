import requests
import logging
from typing import Dict, Any
from .config import LeffaConfig

logger = logging.getLogger(__name__)


def fetch_movies(config: LeffaConfig) -> Dict[str, Any]:
    """Fetch movie data from biosalo.fi API using the daily shows endpoint."""
    url = "https://biosalo.fi/wp-content/plugins/nexxo-scope/public_api.php"
    params = {
        "locationid": config.location_id,
        "action": "exportdailyshows",
        "upcoming": str(config.upcoming_only).lower(),
        "showtype": -1,
        "roomid": -1,
        "contenttypeid": config.content_type_id,
        "lang": config.language,
        "languagecode": "",
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        logger.info(f"Fetched movie data with {len(data.get('shows', {}))} days")
        return data

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch movie data: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to parse movie data: {e}")
        raise

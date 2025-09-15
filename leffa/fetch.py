import requests
import logging
from typing import Dict, Any, List
from .config import LeffaConfig, TheaterConfig

logger = logging.getLogger(__name__)


def fetch_theater_movies(theater: TheaterConfig) -> Dict[str, Any]:
    """Fetch movie data from a theater's API using the daily shows endpoint."""
    url = f"{theater.api_url}/wp-content/plugins/nexxo-scope/public_api.php"
    params = {
        "locationid": theater.location_id,
        "action": "exportdailyshows",
        "upcoming": str(theater.upcoming_only).lower(),
        "showtype": -1,
        "roomid": -1,
        "contenttypeid": theater.content_type_id,
        "lang": theater.language,
        "languagecode": "",
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        logger.info(f"Fetched movie data for {theater.name} with {len(data.get('shows', {}))} days")
        return data

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch movie data for {theater.name}: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to parse movie data for {theater.name}: {e}")
        raise


def fetch_movies(config: LeffaConfig) -> List[Dict[str, Any]]:
    """Fetch movie data from all configured theaters."""
    all_theater_data = []

    for theater in config.theaters:
        try:
            theater_data = fetch_theater_movies(theater)
            theater_data["theater_name"] = theater.name  # Add theater name to response
            theater_data["theater_site_url"] = theater.site_url  # Add site URL for movie links
            theater_data["theater_api_url"] = theater.api_url  # Add API URL for images
            theater_data["theater_movie_path"] = theater.movie_path  # Add movie path
            all_theater_data.append(theater_data)
        except Exception as e:
            logger.error(f"Failed to fetch data for {theater.name}, skipping: {e}")
            # Continue with other theaters even if one fails
            continue

    return all_theater_data

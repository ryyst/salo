import json
from datetime import date
from typing import Any, Optional

from utils.logging import Log
from utils.renderers import save_file


def _read_json_from_file(cache_file: str) -> Optional[str]:
    try:
        with open(cache_file, "r") as f:
            return json.load(f)
    except Exception as e:
        return None


def cache_output(namespace: str, DataModel: Any):
    """Retrieves the given data from cache if it exists, else redownload and save to cache."""

    def decorator(function):
        def wrapper(*args, **kwargs):
            # Import here to avoid circular imports
            from config import get_cache_dir, should_ignore_cache

            today = date.today().strftime("%Y-%m-%d")
            cache_dir = get_cache_dir()
            cache_file = f"{cache_dir}/{today}_{namespace}.json"

            # Check if cache should be ignored
            if should_ignore_cache():
                Log.info("Ignoring cache, forcing redownload...")
            else:
                cached_data = _read_json_from_file(cache_file)
                if cached_data:
                    Log.info("Cached data found! Proceeding offline.")
                    if DataModel == str:
                        return cached_data
                    else:
                        return DataModel(**cached_data)

            Log.info("Missing cache, redownloading...")
            fresh_data = function(*args, **kwargs)

            # Handle both Pydantic models and plain strings/data
            if hasattr(fresh_data, "model_dump_json"):
                cache_content = fresh_data.model_dump_json(indent=2, by_alias=True)
            else:
                cache_content = json.dumps(fresh_data, indent=2)

            save_file(cache_file, cache_content)

            # Return new data and continue with the pipeline as usual
            return fresh_data

        return wrapper

    return decorator

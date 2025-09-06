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
            today = date.today().strftime("%Y-%m-%d")
            cache_file = f"_cache/{today}_{namespace}.json"

            cached_data = _read_json_from_file(cache_file)
            if cached_data:
                Log.info("Cached data found! Proceeding offline.")
                return DataModel(**cached_data)

            Log.info("Missing cache, redownloading...")
            fresh_data = function(*args, **kwargs)

            save_file(cache_file, fresh_data.model_dump_json(indent=2))

            # Return new data and continue with the pipeline as usual
            return fresh_data

        return wrapper

    return decorator

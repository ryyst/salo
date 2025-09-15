import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from collections import defaultdict
from .config import LeffaConfig
from .schema import Movie, MovieShow, LeffaData

logger = logging.getLogger(__name__)


def clean_html_tags(text: str) -> str:
    """Remove HTML tags and clean up text."""
    if not text:
        return ""

    import re

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    # Clean up whitespace
    text = " ".join(text.split())
    # Decode HTML entities
    import html

    text = html.unescape(text)

    return text


def format_duration(duration_minutes: str) -> str:
    """Format duration from minutes to human readable format."""
    try:
        mins = int(duration_minutes)
        hours = mins // 60
        remaining_mins = mins % 60

        if hours > 0:
            return f"{hours}h {remaining_mins}min"
        else:
            return f"{mins}min"
    except (ValueError, TypeError):
        return duration_minutes or ""


def format_premiere_date(premiere_str: str) -> str:
    """Format premiere date to Finnish format."""
    if not premiere_str:
        return ""

    try:
        # Parse the premiere datetime
        premiere_dt = datetime.strptime(premiere_str, "%Y-%m-%d %H:%M:%S")
        # Format to Finnish date format
        return premiere_dt.strftime("%d.%m.%Y")
    except ValueError:
        # If parsing fails, return original or empty
        return premiere_str if premiere_str != "0000-00-00 00:00:00" else ""


def get_relative_premiere_text(premiere_str: str) -> str:
    """Get relative date text like '(5 päivää sitten)' or '(3 päivän päästä)'."""
    if not premiere_str or premiere_str == "0000-00-00 00:00:00":
        return ""

    try:
        # Parse the premiere datetime
        premiere_dt = datetime.strptime(premiere_str, "%Y-%m-%d %H:%M:%S")
        premiere_date = premiere_dt.date()
        today = datetime.now().date()

        # Calculate difference in days
        diff = (premiere_date - today).days

        if diff == 0:
            return "(tänään)"
        elif diff == 1:
            return "(huomenna)"
        elif diff == -1:
            return "(eilen)"
        elif diff > 0:
            return f"({diff} päivän päästä)"
        else:
            return f"({abs(diff)} päivää sitten)"
    except ValueError:
        return ""


def is_premiere_upcoming(premiere_str: str) -> bool:
    """Check if premiere date is in the future."""
    if not premiere_str or premiere_str == "0000-00-00 00:00:00":
        return False

    try:
        premiere_dt = datetime.strptime(premiere_str, "%Y-%m-%d %H:%M:%S")
        premiere_date = premiere_dt.date()
        today = datetime.now().date()
        return premiere_date >= today
    except ValueError:
        return False


def transform_movies(raw_data: Dict[str, Any], config: LeffaConfig) -> LeffaData:
    """Transform raw API data into structured movie listings."""

    shows = raw_data.get("shows", {})

    # Group shows by movie ID
    movies_dict = defaultdict(lambda: {"shows": [], "movie_data": None})

    # Calculate date cutoff (only show movies within config.days_ahead)
    cutoff_date = datetime.now() + timedelta(days=config.days_ahead)

    # Process each day's shows
    for date_str, day_shows in shows.items():
        # Handle empty date string - process all shows regardless of date
        if date_str:
            try:
                show_date = datetime.strptime(date_str, "%Y-%m-%d")
                if show_date > cutoff_date:
                    continue
            except ValueError:
                logger.warning(f"Invalid date format: {date_str}")
                continue
        else:
            logger.info("Processing shows with empty date key")

        for show_data in day_shows:
            movie_id = show_data.get("movieId")
            if not movie_id:
                continue

            # Store movie metadata
            if movies_dict[movie_id]["movie_data"] is None:
                movies_dict[movie_id]["movie_data"] = show_data

            # Create show object
            try:
                show_time = datetime.strptime(
                    show_data.get("startTime", ""), "%Y-%m-%d %H:%M:%S"
                )
                # Finnish weekday abbreviations
                weekdays = ["Ma", "Ti", "Ke", "To", "Pe", "La", "Su"]
                weekday = weekdays[show_time.weekday()]
                formatted_time = f"{weekday} {show_time.strftime('%d.%m. klo %H:%M')}"
                # Split into day and time parts
                paiva = f"{weekday} {show_time.strftime('%d.%m.')}"
                aika = show_time.strftime("%H:%M")
            except ValueError:
                formatted_time = show_data.get("klo", "")
                # Fallback: try to split existing klo format
                if " klo " in formatted_time:
                    parts = formatted_time.split(" klo ")
                    paiva = parts[0]
                    aika = parts[1] if len(parts) > 1 else ""
                else:
                    paiva = ""
                    aika = formatted_time

            show = MovieShow(
                id=show_data.get("showId", ""),
                title=show_data.get("movieTitle", ""),
                start_time=show_data.get("startTime", ""),
                klo=formatted_time,
                paiva=paiva,
                aika=aika,
                room_title=show_data.get("roomTitle", ""),
                duration=format_duration(show_data.get("duration", "")),
                age_limit=show_data.get("agelimit", ""),
                price=show_data.get("priceIncludingTax", ""),
                genre=show_data.get("genre", ""),
                director=show_data.get("director", ""),
                intro=clean_html_tags(show_data.get("intro", "")),
                poster_url=show_data.get("posterurl", ""),
                note=show_data.get("note", ""),
                release_year=show_data.get("release_year", ""),
            )

            movies_dict[movie_id]["shows"].append(show)

    # Convert to final movie objects
    movies = []
    for movie_id, movie_info in movies_dict.items():
        if not movie_info["shows"]:
            continue

        movie_data = movie_info["movie_data"]

        # Sort shows by start time
        sorted_shows = sorted(
            movie_info["shows"], key=lambda s: s.start_time if s.start_time else ""
        )

        premiere_date = movie_data.get("premiere", "")
        movie = Movie(
            id=movie_id,
            title=movie_data.get("movieTitle", ""),
            shows=sorted_shows,
            genre=movie_data.get("genre", ""),
            director=movie_data.get("director", ""),
            intro=clean_html_tags(movie_data.get("intro", "")),
            poster_url=movie_data.get("posterurl", ""),
            duration=format_duration(movie_data.get("duration", "")),
            age_limit=movie_data.get("agelimit", ""),
            release_year=movie_data.get("release_year", ""),
            date_created=movie_data.get("dateCreated", ""),
            premiere_date=premiere_date,
            premiere_formatted=format_premiere_date(premiere_date),
            premiere_relative=get_relative_premiere_text(premiere_date),
            premiere_upcoming=is_premiere_upcoming(premiere_date),
        )

        movies.append(movie)

    # Sort movies by creation date (newest first)
    movies.sort(key=lambda m: m.premiere_date or "", reverse=True)

    logger.info(
        f"Transformed {len(movies)} movies with total {sum(len(m.shows) for m in movies)} shows"
    )

    return LeffaData(
        movies=movies, updated_timestamp=datetime.now().strftime("%d.%m.%Y klo %H:%M")
    )

import logging
import os
from config import register_runner, get_output_dir
from utils.renderers import render_html, save_file
from .config import LeffaConfig
from .fetch import fetch_movies
from .transform import transform_movies

logger = logging.getLogger(__name__)


@register_runner("leffa", LeffaConfig, "Fetch and render movie listings from multiple theaters")
def run_leffa_multi(params: LeffaConfig):
    """Complete ETL pipeline for multiple theater movie listings."""

    logger.info("Starting multi-theater movie listings pipeline")

    # Fetch raw movie data from all theaters
    logger.info(f"Fetching movie data from {len(params.theaters)} theaters")
    all_theater_data = fetch_movies(params)

    # Transform data into structured format
    logger.info("Transforming movie data")
    movie_data = transform_movies(all_theater_data, params)

    # Render to HTML
    logger.info("Rendering movie listings to HTML")
    template_path = "leffa/template.html"
    html = render_html(movie_data, template_path)

    # Use CLI output directory + runner name
    output_dir = os.path.join(get_output_dir(), "leffa")
    output_file = os.path.join(output_dir, "index.html")
    save_file(output_file, html)

    total_movies = sum(len(theater.movies) for theater in movie_data.theaters)
    total_shows = sum(sum(len(m.shows) for m in theater.movies) for theater in movie_data.theaters)

    logger.info(f"✅ Multi-theater movie listings pipeline completed successfully")
    logger.info(f"📁 Output: {output_file}")
    logger.info(f"🎭 Theaters: {len(movie_data.theaters)}")
    logger.info(f"🎬 Total movies: {total_movies}")
    logger.info(f"🎞️ Total shows: {total_shows}")

    return output_file

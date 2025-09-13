import logging
import os
from config import register_runner, get_output_dir
from utils.renderers import render_html, save_file
from .config import LeffaConfig
from .fetch import fetch_movies
from .transform import transform_movies

logger = logging.getLogger(__name__)


@register_runner("leffa", LeffaConfig, "Fetch and render movie listings from Bio Salo")
def run_leffa_salo(params: LeffaConfig):
    """Complete ETL pipeline for Bio Salo movie listings."""

    logger.info("Starting Bio Salo movie listings pipeline")

    # Fetch raw movie data from API
    logger.info("Fetching movie data from biosalo.fi API")
    raw_data = fetch_movies(params)

    # Transform data into structured format
    logger.info("Transforming movie data")
    movie_data = transform_movies(raw_data, params)

    # Render to HTML
    logger.info("Rendering movie listings to HTML")
    template_path = "leffa/template.html"
    html = render_html(movie_data, template_path)

    # Use CLI output directory + runner name
    output_dir = os.path.join(get_output_dir(), "leffa")
    output_file = os.path.join(output_dir, "index.html")
    save_file(output_file, html)

    logger.info(f"✅ Bio Salo movie listings pipeline completed successfully")
    logger.info(f"📁 Output: {output_file}")
    logger.info(f"🎬 Movies: {len(movie_data.movies)}")
    logger.info(f"🎭 Total shows: {sum(len(m.shows) for m in movie_data.movies)}")

    return output_file

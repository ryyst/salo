import logging
from config import register_runner
from .config import LeffaConfig
from .fetch import fetch_movies
from .transform import transform_movies
from .render import render_movies

logger = logging.getLogger(__name__)


@register_runner("leffa_salo", LeffaConfig, "Fetch and render movie listings from Bio Salo")
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
    output_file = render_movies(movie_data, params)
    
    logger.info(f"✅ Bio Salo movie listings pipeline completed successfully")
    logger.info(f"📁 Output: {output_file}")
    logger.info(f"🎬 Movies: {len(movie_data.movies)}")
    logger.info(f"🎭 Total shows: {sum(len(m.shows) for m in movie_data.movies)}")
    
    return output_file
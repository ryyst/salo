import logging
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from .config import LeffaConfig
from .schema import LeffaData

logger = logging.getLogger(__name__)


def render_movies(data: LeffaData, config: LeffaConfig):
    """Render movie data to HTML using Jinja2 template."""
    
    # Setup template environment
    template_dir = Path(__file__).parent
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('template.html')
    
    # Create output directory
    output_dir = Path("_out") / config.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Render template
    html_content = template.render(
        movies=data.movies,
        generated_at=data.generated_at
    )
    
    # Write HTML file
    output_file = output_dir / "index.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    logger.info(f"Rendered movie listings to {output_file}")
    logger.info(f"Generated page with {len(data.movies)} movies")
    
    return str(output_file)
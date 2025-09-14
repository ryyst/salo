from typing import List, Dict, Any
from datetime import datetime
import re

from .config import UuttaConfig


def clean_description(description: str) -> str:
    """Clean HTML and formatting from description text."""
    # Remove HTML tags
    description = re.sub(r"<[^>]+>", "", description)
    # Clean up whitespace and newlines
    description = re.sub(r"\s+", " ", description).strip()
    # Limit length
    if len(description) > 300:
        description = description[:297] + "..."
    return description


def parse_date(date_str: str) -> datetime:
    """Parse RSS date string into datetime object."""
    import email.utils

    # Try to parse the RFC 2822 formatted date (used by RSS)
    # Example: "Sun, 14 Sep 2025 16:50:00 +0000"
    try:
        # Use email.utils.parsedate_to_datetime for RFC 2822 dates
        return email.utils.parsedate_to_datetime(date_str)
    except (ValueError, TypeError):
        pass

    # Fallback formats if the above fails
    date_formats = [
        "%a, %d %b %Y %H:%M:%S %z",  # Standard RFC 822 format
        "%a, %d %b %Y %H:%M:%S",  # Without timezone
        "%Y-%m-%d %H:%M:%S",  # ISO-like format
        "%Y-%m-%dT%H:%M:%S",  # ISO format
    ]

    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    # Fallback to current time if parsing fails
    return datetime.now()


def should_include_article(article: Dict[str, Any], params: UuttaConfig) -> bool:
    """Check if article should be included based on category filtering."""
    categories = article.get("categories", [])

    # Filter out excluded categories (case insensitive)
    for category in categories:
        if category.lower() in params.excluded_categories:
            return False

    return True


def transform_articles(
    sss_articles: List[Dict[str, Any]],
    salo_articles: List[Dict[str, Any]],
    params: UuttaConfig,
) -> Dict[str, Any]:
    """Transform and combine articles from both sources."""
    unified_articles = []
    # sss_articles = sss_articles[: params.max_articles]
    # salo_articles = salo_articles[: params.max_articles]

    # Process SSS articles
    for article in sss_articles:
        if not should_include_article(article, params):
            continue

        try:
            pub_date = parse_date(article.get("pub_date", ""))

            unified_articles.append(
                {
                    "title": article.get("title", ""),
                    "link": article.get("link", ""),
                    "description": clean_description(article.get("description", "")),
                    "pub_date": pub_date,
                    "pub_date_formatted": pub_date.strftime("%d.%m.%Y klo %H:%M"),
                    "source": "sss.fi",
                    "source_label": "sss.fi",
                    "categories": article.get("categories", []),
                    "thumbnail_url": article.get(
                        "media_url", ""
                    ),  # Use actual media URL from RSS
                }
            )
        except Exception as e:
            continue  # Skip malformed articles

    # Process Salo tiedotteet articles
    for article in salo_articles:
        if not should_include_article(article, params):
            continue

        try:
            pub_date = parse_date(article.get("pub_date", ""))

            unified_articles.append(
                {
                    "title": article.get("title", ""),
                    "link": article.get("link", ""),
                    "description": clean_description(article.get("description", "")),
                    "pub_date": pub_date,
                    "pub_date_formatted": pub_date.strftime("%d.%m.%Y klo %H:%M"),
                    "source": "salo_tiedotteet",
                    "source_label": "Salo",
                    "categories": article.get("categories", []),
                    "thumbnail_url": "https://tiedotteet.salo.fi/wp-content/uploads/sites/4/2020/09/Salo_RGB.jpg",  # Salo logo
                }
            )
        except Exception as e:
            continue  # Skip malformed articles

    # Sort by publication date (newest first)
    unified_articles.sort(key=lambda x: x["pub_date"], reverse=True)

    return {
        "articles": unified_articles,
        "total_count": len(unified_articles),
        "sss_count": len([a for a in unified_articles if a["source"] == "sss.fi"]),
        "salo_count": len(
            [a for a in unified_articles if a["source"] == "salo_tiedotteet"]
        ),
        "updated_timestamp": datetime.now().strftime("%d.%m.%Y klo %H:%M"),
    }

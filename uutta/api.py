from utils.baseapi import BaseAPI
from utils.logging import Log

import xml.etree.ElementTree as ET
from typing import List, Dict, Any


class RSSFetcher(BaseAPI):
    """RSS feed fetcher that extends BaseAPI."""

    def __init__(self, rss_url: str):
        super().__init__("", headers={"Accept": "application/xml,text/xml,*/*"})
        self.rss_url = rss_url

    def fetch_rss(self) -> List[Dict[str, Any]]:
        """Fetch and parse RSS feed."""
        response = self.request("GET", self.rss_url, useJSON=False)

        if not response.ok:
            Log.error(f"Failed to fetch RSS from {self.rss_url}: {response.status}")
            return []

        try:
            root = ET.fromstring(response.data)
            items = []

            # Handle RSS 2.0 format
            for item in root.findall(".//item"):
                title_elem = item.find("title")
                link_elem = item.find("link")
                description_elem = item.find("description")
                pubdate_elem = item.find("pubDate")
                category_elems = item.findall("category")
                enclosure_elem = item.find("enclosure")

                # Try to find media content elements (with namespace handling)
                media_content = item.find(".//*[@url][@medium='image']")
                if media_content is None:
                    media_content = item.find(".//enclosure[@type]")

                # Extract text content, handling CDATA
                def get_text(elem):
                    if elem is None:
                        return ""
                    text = elem.text or ""
                    # Clean up common HTML entities in descriptions
                    return text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")

                # Extract media URL from enclosure or media:content elements
                media_url = ""
                if enclosure_elem is not None and enclosure_elem.get("url"):
                    media_url = enclosure_elem.get("url", "")
                elif media_content is not None and media_content.get("url"):
                    media_url = media_content.get("url", "")

                article = {
                    "title": get_text(title_elem),
                    "link": get_text(link_elem),
                    "description": get_text(description_elem),
                    "pub_date": get_text(pubdate_elem),
                    "categories": [get_text(cat) for cat in category_elems],
                    "media_url": media_url,
                }

                if article["title"] and article["link"]:
                    items.append(article)

            Log.debug(f"Fetched {len(items)} articles from {self.rss_url}")
            return items

        except ET.ParseError as e:
            Log.error(f"Failed to parse RSS XML from {self.rss_url}: {e}")
            return []

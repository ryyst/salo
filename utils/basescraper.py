from bs4 import BeautifulSoup
from utils.baseapi import BaseAPI


class BaseScraper(BaseAPI):
    """HTML scraper that extends BaseAPI with BeautifulSoup parsing."""

    def __init__(self, base_url: str, headers=None):
        # Set up HTML-appropriate headers
        html_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        if headers:
            html_headers.update(headers)

        super().__init__(base_url, html_headers)

    def get_html(self, endpoint: str, css_selector: str, config=None):
        """Fetch HTML and extract content from CSS selector."""
        # Use BaseAPI's request method with useJSON=False to get raw HTML
        response = self.request("GET", endpoint, config, useJSON=False)

        if not response.ok:
            return ""

        # Parse HTML and extract CSS selector content
        soup = BeautifulSoup(response.data, "html.parser")
        elements = soup.select(css_selector)

        if elements:
            return elements[0].get_text(strip=True)
        else:
            return ""

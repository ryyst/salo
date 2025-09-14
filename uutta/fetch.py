from utils.cache import cache_output

from .config import UuttaConfig
from .schema import RawRSSData
from .api import RSSFetcher


@cache_output("uutta_sss_raw", RawRSSData)
def fetch_sss_rss(params: UuttaConfig) -> RawRSSData:
    """Fetch articles from SSS.fi RSS feed."""
    fetcher = RSSFetcher(params.sss_rss_url)
    articles = fetcher.fetch_rss()
    return RawRSSData(articles=articles)


@cache_output("uutta_salo_raw", RawRSSData)
def fetch_salo_rss(params: UuttaConfig) -> RawRSSData:
    """Fetch articles from Salo tiedotteet RSS feed."""
    fetcher = RSSFetcher(params.salo_rss_url)
    articles = fetcher.fetch_rss()
    return RawRSSData(articles=articles)

import logging
from typing import Dict, Any

from app.scraper.engine import scraper_engine
from app.scraper.extractors.mutual_fund import extract_mutual_fund
from app.scraper.extractors.amc import extract_amc
from app.scraper.extractors.nfo import extract_nfo
from app.scraper.extractors.market_news import extract_market_news
from app.scraper.extractors.filter_page import extract_filter_page

logger = logging.getLogger(__name__)

async def scrape_and_extract(url: str, source_type: str) -> Dict[str, Any]:
    """
    Orchestrates the scraping and extraction process based on source_type.
    """
    logger.info(f"Scraping URL: {url} of type {source_type}")
    
    # 1. Fetch HTML using the Playwright engine
    html = await scraper_engine.get_rendered_html(url)
    
    # 2. Route to the appropriate extractor
    if source_type == "mutual_fund":
        data = extract_mutual_fund(html, url)
    elif source_type == "amc":
        data = extract_amc(html, url)
    elif source_type == "nfo":
        data = extract_nfo(html, url)
    elif source_type == "market_news":
        data = extract_market_news(html, url)
    elif source_type == "filter":
        data = extract_filter_page(html, url)
    else:
        logger.warning(f"Unknown source_type '{source_type}'. Using empty extraction.")
        data = {}
        
    return data

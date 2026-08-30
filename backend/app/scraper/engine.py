"""
Playwright-based Resilient Scraper Engine.
Architecture reference: §1.2 (Scraper Engine Core) and §2.1 (Implementation Plan).
"""

import logging
import asyncio
from typing import Optional, Dict, Any
from urllib.parse import urlparse

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Error as PlaywrightError

from app.config import settings

logger = logging.getLogger(__name__)


class ScrapeFailedError(Exception):
    """Custom exception raised when a scrape attempt fails completely after all retries."""
    pass


class ResilientScraper:
    """
    Manages Playwright browser lifecycle and context pool for concurrent scraping.
    """
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self._context_pool = asyncio.Queue(maxsize=settings.SCRAPE_MAX_CONCURRENT)
        self._contexts: list[BrowserContext] = []

    async def initialize(self) -> None:
        """Launch the headless Chromium browser and initialize the context pool."""
        logger.info("Initializing Playwright Chromium browser...")
        self.playwright = await async_playwright().start()
        
        # Chromium headless with stealth-like arguments
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-extensions",
            ]
        )
        
        # Create a pool of reusable contexts to avoid overhead of creating contexts per request
        for _ in range(settings.SCRAPE_MAX_CONCURRENT):
            context = await self.browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
                java_script_enabled=True,
                bypass_csp=True,
            )
            # Block media to save bandwidth/speed up loading
            await context.route("**/*", self._block_unnecessary_resources)
            self._contexts.append(context)
            await self._context_pool.put(context)
            
        logger.info(f"Initialized browser with {settings.SCRAPE_MAX_CONCURRENT} concurrent contexts.")

    async def _block_unnecessary_resources(self, route):
        """Block images, fonts, and media to speed up page load."""
        if route.request.resource_type in ("image", "media", "font", "stylesheet"):
            await route.abort()
        else:
            await route.continue_()

    async def shutdown(self) -> None:
        """Close all contexts and the browser."""
        logger.info("Shutting down Playwright browser...")
        for context in self._contexts:
            try:
                await context.close()
            except Exception as e:
                logger.warning(f"Error closing context: {e}")
                
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Browser shut down successfully.")

    async def get_rendered_html(self, url: str) -> str:
        """
        Fetch the rendered HTML for a given URL, utilizing the context pool.
        Includes a 2-retry mechanism with exponential backoff.
        """
        max_retries = 2
        timeout = settings.SCRAPE_TIMEOUT_SECONDS * 1000  # Playwright uses milliseconds

        for attempt in range(1, max_retries + 2):
            context = await self._context_pool.get()
            page = None
            try:
                page = await context.new_page()
                logger.debug(f"[{attempt}/{max_retries+1}] Fetching {url}")
                
                # Navigate and wait for network idle to ensure JS framework finishes rendering
                response = await page.goto(
                    url, 
                    timeout=timeout, 
                    wait_until="load"
                )
                
                if response and not response.ok:
                    raise PlaywrightError(f"HTTP {response.status} - {response.status_text}")
                
                # Wait briefly for any late-stage DOM mutations (e.g. React hydration)
                await page.wait_for_timeout(2000)
                
                content = await page.content()
                logger.debug(f"Successfully fetched {len(content)} bytes from {url}")
                return content
                
            except PlaywrightError as e:
                logger.warning(f"Attempt {attempt} failed for {url}: {str(e)}")
                if attempt > max_retries:
                    raise ScrapeFailedError(f"Failed to scrape {url} after {max_retries} retries: {str(e)}")
                await asyncio.sleep(5 * attempt)  # Backoff
            finally:
                if page:
                    await page.close()
                await self._context_pool.put(context)


# Global singleton instance for use in FastAPI app lifespan
scraper_engine = ResilientScraper()

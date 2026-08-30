import asyncio
import json
from app.scraper.engine import scraper_engine
from app.scraper.extractors.mutual_fund import extract_mutual_fund
from app.scraper.extractors.market_news import extract_market_news

async def main():
    print("Initializing scraper engine...")
    await scraper_engine.initialize()
    
    urls = [
        # Mutual fund
        ("https://groww.in/mutual-funds/hdfc-mid-cap-opportunities-fund-direct-growth", "mutual_fund"),
        # Market news
        ("https://groww.in/share-market-today", "market_news"),
    ]
    
    for url, page_type in urls:
        print(f"\n--- Scraping {url} ---")
        try:
            html = await scraper_engine.get_rendered_html(url)
            print(f"Fetched HTML, size: {len(html)} bytes")
            
            if page_type == "mutual_fund":
                data = extract_mutual_fund(html, url)
                filename_prefix = "scratch_data/mutual_fund"
            elif page_type == "market_news":
                data = extract_market_news(html, url)
                filename_prefix = "scratch_data/market_news"
                
            # Save raw HTML
            with open(f"{filename_prefix}_raw.html", "w", encoding="utf-8") as f:
                f.write(html)
            
            # Save normalized JSON
            with open(f"{filename_prefix}_normalized.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
                
            print(f"Saved {filename_prefix}_raw.html and {filename_prefix}_normalized.json")
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            
    print("\nShutting down engine...")
    await scraper_engine.shutdown()

if __name__ == "__main__":
    asyncio.run(main())

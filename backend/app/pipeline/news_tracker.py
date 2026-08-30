import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import NewsTracking
from app.pipeline.change_detector import compute_content_hash

logger = logging.getLogger(__name__)

def _now() -> datetime:
    return datetime.now(timezone.utc)

class NewsTracker:
    async def process_news(self, session: AsyncSession, extracted_data: Any):
        """
        Process newly scraped News data.
        extracted_data is expected to be a list of news dictionaries.
        """
        if not isinstance(extracted_data, list):
            extracted_data = [extracted_data]
            
        logger.info(f"Processing {len(extracted_data)} news items in NewsTracker")
        
        current_time = _now()
        
        for news in extracted_data:
            title = news.get("title")
            if not title:
                continue
                
            news_hash = compute_content_hash(news)
            source_url = news.get("link", "")
            summary = news.get("summary", "")
            
            # The published time from source is string, we'll try to parse it if needed, or leave it.
            # But the schema says DateTime. Let's just use current time if we can't parse it easily.
            # Usually news has a relative time like "2h ago".
            
            # Check if this News already exists
            stmt = select(NewsTracking).where(NewsTracking.title == title)
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing:
                # Update last_seen_at
                existing.last_seen_at = current_time
                
                # Check for content change
                if existing.content_hash != news_hash:
                    logger.info(f"News '{title}' has changed")
                    existing.content_hash = news_hash
                    existing.summary = summary
                    existing.source_url = source_url
                    existing.is_new = True # Flag as changed
                    existing.notified = False
            else:
                # Insert new News
                logger.info(f"Found new news: {title}")
                new_news = NewsTracking(
                    title=title,
                    source_url=source_url,
                    summary=summary,
                    published_at=current_time, # Fallback
                    first_seen_at=current_time,
                    last_seen_at=current_time,
                    content_hash=news_hash,
                    is_new=True,
                    notified=False
                )
                session.add(new_news)

news_tracker = NewsTracker()

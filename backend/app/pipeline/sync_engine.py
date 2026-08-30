import logging
import asyncio
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.models.db_models import SourceURL, RefreshStatus, ScrapeHistory
from app.scraper.engine import ScrapeFailedError
from app.scraper.router import scrape_and_extract
from app.pipeline.change_detector import compute_content_hash
from app.pipeline.snapshot_manager import snapshot_manager
from app.pipeline.chunker import chunker
from app.pipeline.embedder import embedder
from app.pipeline.nfo_tracker import nfo_tracker
from app.pipeline.news_tracker import news_tracker

logger = logging.getLogger(__name__)

def _now() -> datetime:
    return datetime.now(timezone.utc)

class SyncEngine:
    """
    Implements the 5-state synchronization decision matrix.
    Architecture reference: §8 (Synchronization Engine) and §3.5 of Implementation Plan.
    """

    async def run_sync_cycle(self, trigger_type: str = "scheduler"):
        """
        Runs a full synchronization cycle for all URLs.
        """
        logger.info(f"Starting sync cycle (trigger: {trigger_type})")
        
        async with AsyncSessionLocal() as session:
            try:
                # 1. Handle DELETED sources
                await self._handle_deleted_sources(session)
                
                # 2. Get active URLs
                stmt = select(SourceURL).where(SourceURL.is_active == True)
                result = await session.execute(stmt)
                active_urls = result.scalars().all()
                
                # 3. Process each active URL
                # Running sequentially to not overwhelm memory/CPU with chunking/embedding, 
                # but Playwright handles its own concurrency in ScraperEngine if we did gather.
                for source in active_urls:
                    await self._process_source(session, source, trigger_type)
                    
                await session.commit()
                logger.info("Sync cycle completed successfully")
                
                return {"status": "success", "processed": len(active_urls)}
            except Exception as e:
                logger.error(f"Sync cycle failed: {e}")
                await session.rollback()
                return {"status": "error", "message": str(e)}

    async def _handle_deleted_sources(self, session: AsyncSession):
        """
        Finds URLs that are inactive but still have 'success' status or vectors,
        and cleans them up (DELETED path).
        """
        stmt = select(SourceURL).where(SourceURL.is_active == False)
        result = await session.execute(stmt)
        deleted_urls = result.scalars().all()
        
        for source in deleted_urls:
            # Delete vectors
            embedder.delete_by_source(source.id)
            # Delete snapshots
            snapshot_manager.delete_snapshots(source.id)
            
            # The refresh_status and scrape_history might be cascade deleted or kept for audit.
            # Usually we don't need to do anything else if vectors and snapshots are gone.
            logger.info(f"Cleaned up vectors and snapshots for DELETED source {source.id}")

    async def _process_source(self, session: AsyncSession, source: SourceURL, trigger_type: str):
        """
        Processes a single source URL: Scrape -> Hash -> Chunk -> Embed
        """
        logger.info(f"Processing source {source.id}: {source.url}")
        
        # Get or create refresh_status
        stmt = select(RefreshStatus).where(RefreshStatus.source_url_id == source.id)
        result = await session.execute(stmt)
        refresh_status = result.scalar_one_or_none()
        
        if not refresh_status:
            refresh_status = RefreshStatus(source_url_id=source.id)
            session.add(refresh_status)
            
        start_time = _now()
        
        try:
            # a. Attempt scrape
            extracted_data = await scrape_and_extract(source.url, source.source_type)
            
            if not extracted_data:
                raise ScrapeFailedError("Extractor returned empty data")
                
            # c. Compute hash
            new_hash = compute_content_hash(extracted_data)
            
            # d. Check if UNCHANGED
            if refresh_status.content_hash == new_hash:
                logger.info(f"Source {source.id} is UNCHANGED")
                # UNCHANGED path
                refresh_status.last_attempt_at = _now()
                refresh_status.current_status = "unchanged"
                
                self._record_history(session, source.id, "unchanged", trigger_type, new_hash, duration=(_now() - start_time).total_seconds())
                
            else:
                is_new = refresh_status.content_hash is None
                logger.info(f"Source {source.id} is {'NEW' if is_new else 'CHANGED'}")
                
                # e. CHANGED / NEW path
                
                # Snapshots
                if not is_new:
                    snapshot_manager.rotate(source.id)
                    
                snapshot_manager.save_current(source.id, extracted_data)
                
                if not is_new:
                    snapshot_manager.compute_diff(source.id)
                
                # Phase 7 Trackers
                if source.source_type == "nfo":
                    await nfo_tracker.process_nfo(session, extracted_data)
                elif source.source_type == "market_news":
                    await news_tracker.process_news(session, extracted_data)
                
                # Chunking
                chunks, metadatas = chunker.chunk_data(source.source_type, extracted_data)
                
                # Embedding
                if not is_new:
                    # Delete old vectors first
                    embedder.delete_by_source(source.id)
                    
                embedder.embed_and_store(source.id, source.source_type, chunks, metadatas)
                
                # Update DB
                refresh_status.last_attempt_at = _now()
                refresh_status.last_success_at = _now()
                refresh_status.current_status = "success"
                refresh_status.content_hash = new_hash
                refresh_status.error_message = None
                refresh_status.error_count = 0
                
                self._record_history(session, source.id, "success", trigger_type, new_hash, duration=(_now() - start_time).total_seconds())

        except ScrapeFailedError as e:
            # b. FAILED path
            logger.warning(f"Source {source.id} FAILED: {str(e)}")
            refresh_status.last_attempt_at = _now()
            refresh_status.current_status = "failed"
            refresh_status.error_count += 1
            refresh_status.error_message = str(e)
            
            self._record_history(session, source.id, "failed", trigger_type, error_message=str(e), duration=(_now() - start_time).total_seconds())
            
        except Exception as e:
            # Unexpected error
            logger.error(f"Unexpected error processing source {source.id}: {e}")
            refresh_status.last_attempt_at = _now()
            refresh_status.current_status = "failed"
            refresh_status.error_count += 1
            refresh_status.error_message = f"Unexpected error: {str(e)}"
            
            self._record_history(session, source.id, "failed", trigger_type, error_message=str(e), duration=(_now() - start_time).total_seconds())

    def _record_history(self, session: AsyncSession, source_url_id: int, status: str, trigger_type: str, content_hash: str = None, error_message: str = None, duration: float = None):
        """Records a scrape history entry."""
        history = ScrapeHistory(
            source_url_id=source_url_id,
            scraped_at=_now(),
            status=status,
            trigger_type=trigger_type,
            content_hash=content_hash,
            error_message=error_message,
            duration_ms=int(duration * 1000) if duration else None
        )
        session.add(history)

# Global singleton
sync_engine = SyncEngine()

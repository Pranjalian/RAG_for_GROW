import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import NFOTracking
from app.pipeline.change_detector import compute_content_hash

logger = logging.getLogger(__name__)

def _now() -> datetime:
    return datetime.now(timezone.utc)

class NFOTracker:
    async def process_nfo(self, session: AsyncSession, extracted_data: Any):
        """
        Process newly scraped NFO data.
        extracted_data is expected to be a list of NFO dictionaries.
        """
        if not isinstance(extracted_data, list):
            extracted_data = [extracted_data]
            
        logger.info(f"Processing {len(extracted_data)} NFOs in NFOTracker")
        
        current_time = _now()
        
        for nfo in extracted_data:
            nfo_name = nfo.get("fund_name")
            if not nfo_name:
                continue
                
            nfo_hash = compute_content_hash(nfo)
            status = nfo.get("status", "unknown")
            amc = nfo.get("amc_name", "")
            
            # Check if this NFO already exists
            stmt = select(NFOTracking).where(NFOTracking.nfo_name == nfo_name)
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing:
                # Update last_seen_at
                existing.last_seen_at = current_time
                
                # Check for content change
                if existing.content_hash != nfo_hash:
                    logger.info(f"NFO {nfo_name} has changed")
                    existing.last_changed_at = current_time
                    existing.content_hash = nfo_hash
                    existing.status = status
                    existing.amc = amc
                    existing.is_new = True # Flag as new/changed for notifications
                    existing.notified = False
            else:
                # Insert new NFO
                logger.info(f"Found new NFO: {nfo_name}")
                new_nfo = NFOTracking(
                    nfo_name=nfo_name,
                    amc=amc,
                    status=status,
                    first_seen_at=current_time,
                    last_seen_at=current_time,
                    last_changed_at=current_time,
                    content_hash=nfo_hash,
                    is_new=True,
                    notified=False
                )
                session.add(new_nfo)

nfo_tracker = NFOTracker()

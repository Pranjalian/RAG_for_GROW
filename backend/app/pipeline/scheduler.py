import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.config import settings
from app.pipeline.sync_engine import sync_engine

logger = logging.getLogger(__name__)

# Create the scheduler instance
scheduler = AsyncIOScheduler()

def start_scheduler():
    """Starts the APScheduler for the sync engine."""
    logger.info(f"Starting scheduler with interval: {settings.SCRAPE_INTERVAL_MINUTES} minutes")
    
    scheduler.add_job(
        sync_engine.run_sync_cycle,
        trigger=IntervalTrigger(minutes=settings.SCRAPE_INTERVAL_MINUTES),
        kwargs={"trigger_type": "scheduler"},
        id="auto_refresh",
        replace_existing=True,
    )
    scheduler.start()

async def trigger_manual_sync():
    """Called by admin API to run immediate sync."""
    logger.info("Manual sync triggered via Admin API")
    return await sync_engine.run_sync_cycle(trigger_type="admin_manual")

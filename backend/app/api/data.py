"""
Data router — public read endpoints for funds, freshness, notifications,
watchlist, and notification preferences.
"""

import logging
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from pydantic import BaseModel

from app.db.session import AsyncSessionLocal
from app.models.db_models import SourceURL, RefreshStatus
from app.api.deps import AsyncSession, get_db
from app.models.schemas import FreshnessResponse
from app.pipeline.snapshot_manager import snapshot_manager

logger = logging.getLogger(__name__)
router = APIRouter()

def _now() -> datetime:
    return datetime.now(timezone.utc)

@router.get("/freshness", response_model=FreshnessResponse)
async def get_freshness(db: AsyncSession = Depends(get_db)):
    """
    Returns current data freshness status across all sources.
    """
    result = await db.execute(
        select(RefreshStatus.current_status, func.count(RefreshStatus.id))
        .join(SourceURL, SourceURL.id == RefreshStatus.source_url_id)
        .where(SourceURL.is_active == True)
        .group_by(RefreshStatus.current_status)
    )
    
    counts = dict(result.all())
    
    healthy = counts.get("success", 0) + counts.get("unchanged", 0)
    failed = counts.get("failed", 0)
    total = sum(counts.values())
    
    # Just a simple aggregate for now
    status = "healthy" if failed == 0 and healthy > 0 else "failed" if healthy == 0 and total > 0 else "stale"
    if total == 0:
        status = "unavailable"
        
    # Get last refresh time across all
    last_refresh_res = await db.execute(
        select(func.max(RefreshStatus.last_attempt_at))
        .join(SourceURL, SourceURL.id == RefreshStatus.source_url_id)
        .where(SourceURL.is_active == True)
    )
    last_refresh = last_refresh_res.scalar_one_or_none()

    return FreshnessResponse(
        status=status,
        total_sources=total,
        healthy_count=healthy,
        stale_count=0, # Simplified
        failed_count=failed,
        refresh_in_progress=False,
        last_refresh=last_refresh
    )


@router.get("/funds")
async def list_funds(db: AsyncSession = Depends(get_db)):
    """
    Returns list of all scraped fund names available for comparison/search.
    """
    result = await db.execute(
        select(SourceURL).where(
            SourceURL.is_active == True,
            SourceURL.source_type == "mutual_fund",
        )
    )
    sources = result.scalars().all()
    return {"funds": [{"id": s.id, "label": s.label, "url": s.url} for s in sources]}

class CompareRequest(BaseModel):
    fund_ids: List[int]

@router.post("/compare")
async def compare_funds(req: CompareRequest):
    """
    Compare multiple funds by returning their current snapshots side-by-side.
    """
    results = []
    for fid in req.fund_ids:
        snap = snapshot_manager.get_current(fid)
        if snap:
            results.append({"fund_id": fid, "data": snap})
    return {"comparisons": results}

@router.get("/nfo")
async def list_nfos(db: AsyncSession = Depends(get_db)):
    """
    Returns all NFO data from tracking table.
    """
    from app.models.db_models import NFOTracking
    result = await db.execute(select(NFOTracking).order_by(NFOTracking.last_seen_at.desc()))
    nfos = result.scalars().all()
    
    return {"nfos": [{
        "id": nfo.id,
        "fund_name": nfo.nfo_name,
        "amc_name": nfo.amc,
        "status": nfo.status,
        "is_new": nfo.is_new,
        "open_date": nfo.open_date,
        "close_date": nfo.close_date,
        "last_changed_at": nfo.last_changed_at
    } for nfo in nfos]}

@router.get("/news")
async def list_news(db: AsyncSession = Depends(get_db)):
    """
    Returns all news data from tracking table.
    """
    from app.models.db_models import NewsTracking
    result = await db.execute(select(NewsTracking).order_by(NewsTracking.published_at.desc(), NewsTracking.last_seen_at.desc()))
    news = result.scalars().all()
    
    return {"news": [{
        "id": item.id,
        "title": item.title,
        "summary": item.summary,
        "link": item.source_url,
        "is_new": item.is_new,
        "published_at": item.published_at
    } for item in news]}

# --- Notifications ---

@router.get("/notifications")
async def get_notifications(session_id: str = Query(...), db: AsyncSession = Depends(get_db)):
    from app.models.db_models import NotificationPref, NFOTracking, NewsTracking
    
    # 1. Get user prefs
    stmt = select(NotificationPref).where(NotificationPref.session_id == session_id)
    result = await db.execute(stmt)
    prefs = result.scalar_one_or_none()
    
    notify_nfo = prefs.notify_new_nfo if prefs else False
    notify_news = prefs.notify_news if prefs else False
    
    notifications = []
    
    # 2. Get new NFOs
    if notify_nfo:
        stmt_nfo = select(NFOTracking).where(NFOTracking.is_new == True)
        result_nfo = await db.execute(stmt_nfo)
        for nfo in result_nfo.scalars().all():
            notifications.append({
                "id": f"nfo_{nfo.id}",
                "type": "nfo",
                "title": f"New/Changed NFO: {nfo.nfo_name}",
                "summary": f"Status: {nfo.status}, AMC: {nfo.amc}",
                "timestamp": nfo.last_changed_at or nfo.first_seen_at
            })
            
    # 3. Get new News
    if notify_news:
        stmt_news = select(NewsTracking).where(NewsTracking.is_new == True)
        result_news = await db.execute(stmt_news)
        for news in result_news.scalars().all():
            notifications.append({
                "id": f"news_{news.id}",
                "type": "news",
                "title": f"Latest News: {news.title}",
                "summary": news.summary,
                "timestamp": news.published_at or news.first_seen_at
            })
            
    # Sort by timestamp descending
    notifications.sort(key=lambda x: x["timestamp"] or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    
    return {"notifications": notifications}

# --- Watchlist ---

class WatchlistAddRequest(BaseModel):
    session_id: str
    item_type: str
    item_identifier: str
    label: str

@router.get("/watchlist")
async def get_watchlist(session_id: str = Query(...), db: AsyncSession = Depends(get_db)):
    from app.models.db_models import WatchlistItem
    
    result = await db.execute(select(WatchlistItem).where(WatchlistItem.session_id == session_id))
    items = result.scalars().all()
    
    enriched_items = []
    for item in items:
        data = {}
        if item.item_type == "mutual_fund" and item.item_identifier.isdigit():
            data = snapshot_manager.get_current(int(item.item_identifier)) or {}
            
        enriched_items.append({
            "id": item.id,
            "item_type": item.item_type,
            "item_identifier": item.item_identifier,
            "label": item.label,
            "added_at": item.added_at,
            "data": data
        })
        
    return {"watchlist": enriched_items}

@router.post("/watchlist")
async def add_to_watchlist(req: WatchlistAddRequest, db: AsyncSession = Depends(get_db)):
    from app.models.db_models import WatchlistItem
    
    # Check if already exists
    stmt = select(WatchlistItem).where(
        WatchlistItem.session_id == req.session_id,
        WatchlistItem.item_identifier == req.item_identifier
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        return {"message": "Already in watchlist"}
        
    new_item = WatchlistItem(
        session_id=req.session_id,
        item_type=req.item_type,
        item_identifier=req.item_identifier,
        label=req.label
    )
    db.add(new_item)
    await db.commit()
    return {"message": "Added to watchlist"}

@router.delete("/watchlist/{item_id}")
async def remove_from_watchlist(item_id: int, session_id: str = Query(...), db: AsyncSession = Depends(get_db)):
    from app.models.db_models import WatchlistItem
    
    stmt = select(WatchlistItem).where(
        WatchlistItem.id == item_id,
        WatchlistItem.session_id == session_id
    )
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    
    if item:
        await db.delete(item)
        await db.commit()
        return {"message": "Removed from watchlist"}
    return {"message": "Item not found"}

# --- Notification Preferences ---

@router.get("/notification-prefs")
async def get_notification_prefs(session_id: str = Query(...), db: AsyncSession = Depends(get_db)):
    from app.models.db_models import NotificationPref
    stmt = select(NotificationPref).where(NotificationPref.session_id == session_id)
    result = await db.execute(stmt)
    prefs = result.scalar_one_or_none()
    
    if not prefs:
        return {"session_id": session_id, "notify_new_nfo": False, "notify_news": False, "topics": []}
        
    return {
        "session_id": prefs.session_id,
        "notify_new_nfo": prefs.notify_new_nfo,
        "notify_news": prefs.notify_news,
        "topics": prefs.topics or []
    }

class NotificationPrefUpdate(BaseModel):
    session_id: str
    notify_new_nfo: bool
    notify_news: bool
    topics: list = []

@router.put("/notification-prefs")
async def update_notification_prefs(req: NotificationPrefUpdate, db: AsyncSession = Depends(get_db)):
    from app.models.db_models import NotificationPref
    
    stmt = select(NotificationPref).where(NotificationPref.session_id == req.session_id)
    result = await db.execute(stmt)
    prefs = result.scalar_one_or_none()
    
    if prefs:
        prefs.notify_new_nfo = req.notify_new_nfo
        prefs.notify_news = req.notify_news
        prefs.topics = req.topics
    else:
        prefs = NotificationPref(
            session_id=req.session_id,
            notify_new_nfo=req.notify_new_nfo,
            notify_news=req.notify_news,
            topics=req.topics
        )
        db.add(prefs)
        
    await db.commit()
    return {"message": "Preferences updated"}

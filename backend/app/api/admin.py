"""
Admin router — protected endpoints for URL management, sync control,
and status monitoring.
All endpoints require a valid JWT (Depends(verify_jwt)).
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, desc
from pydantic import BaseModel

from app.api.deps import AsyncSession, get_db, verify_jwt
from app.auth.jwt_handler import create_access_token
from app.auth.password import verify_password
from app.config import settings
from app.models.db_models import AdminUser, RefreshStatus, SourceURL, ScrapeHistory
from app.models.schemas import (
    AdminLoginRequest,
    AdminLoginResponse,
    SourceURLCreate,
    SourceURLResponse,
    SyncTriggerResponse,
    ScrapeHistoryResponse,
    RefreshStatusResponse
)
from app.pipeline.scheduler import trigger_manual_sync

logger = logging.getLogger(__name__)
router = APIRouter()

# ── Auth ──────────────────────────────────────────────────────────────────────

@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(
    body: AdminLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Admin login. Returns a JWT access token on success.
    Rate limited: 10 req/min (applied via slowapi in main.py).
    """
    result = await db.execute(
        select(AdminUser).where(AdminUser.username == body.username)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    token = create_access_token({"sub": user.username})
    return AdminLoginResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRY_HOURS * 3600,
    )


# ── Source URL Management ─────────────────────────────────────────────────────

@router.get("/urls", response_model=list[SourceURLResponse])
async def list_urls(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_jwt),
):
    """List all active source URLs."""
    result = await db.execute(
        select(SourceURL).where(SourceURL.is_active == True).order_by(SourceURL.added_at)
    )
    return result.scalars().all()


@router.post("/urls", response_model=SourceURLResponse, status_code=status.HTTP_201_CREATED)
async def add_url(
    body: SourceURLCreate,
    db: AsyncSession = Depends(get_db),
    token_data: dict = Depends(verify_jwt),
):
    """
    Add a new source URL. Must be from the groww.in domain.
    """
    url_str = body.url.lower()
    if not url_str.startswith("https://groww.in/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only groww.in URLs are permitted. Must start with https://groww.in/",
        )
        
    permitted_paths = ["/mutual-funds/", "/nfo", "/share-market-today"]
    path = url_str.replace("https://groww.in", "")
    if not any(path.startswith(p) for p in permitted_paths):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"URL path must start with one of: {permitted_paths}",
        )

    existing = await db.execute(
        select(SourceURL).where(SourceURL.url == body.url, SourceURL.is_active == True)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This URL is already an active source.",
        )

    source = SourceURL(
        url=body.url,
        source_type=body.source_type,
        label=body.label,
        is_active=True,
        added_by=token_data.get("sub", "admin"),
    )
    db.add(source)
    await db.flush()

    refresh = RefreshStatus(source_url_id=source.id, current_status="pending")
    db.add(refresh)
    await db.commit()
    await db.refresh(source)
    return source

class SourceURLUpdate(BaseModel):
    url: Optional[str] = None
    source_type: Optional[str] = None
    label: Optional[str] = None

@router.put("/urls/{url_id}", response_model=SourceURLResponse)
async def update_url(
    url_id: int,
    body: SourceURLUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_jwt),
):
    """Update an existing source URL."""
    result = await db.execute(
        select(SourceURL).where(SourceURL.id == url_id, SourceURL.is_active == True)
    )
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found.")
        
    if body.url is not None:
        if not body.url.lower().startswith("https://groww.in/"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only groww.in URLs permitted.")
        source.url = body.url
    if body.source_type is not None:
        source.source_type = body.source_type
    if body.label is not None:
        source.label = body.label
        
    await db.commit()
    await db.refresh(source)
    return source


@router.delete("/urls/{url_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_url(
    url_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_jwt),
):
    """Soft-delete a source URL (sets is_active=False, removed_at=now)."""
    result = await db.execute(
        select(SourceURL).where(SourceURL.id == url_id, SourceURL.is_active == True)
    )
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found.")

    source.is_active = False
    source.removed_at = datetime.now(timezone.utc)
    await db.commit()


# ── Sync Control ──────────────────────────────────────────────────────────────

@router.post("/sync", response_model=SyncTriggerResponse)
async def trigger_sync(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_jwt),
):
    """
    Trigger a manual full sync cycle.
    """
    stats = await trigger_manual_sync()
    
    return SyncTriggerResponse(
        message="Manual sync complete",
        trigger_type="admin_manual",
        total=stats.get("total", 0),
        success=stats.get("success", 0),
        failed=stats.get("failed", 0),
        unchanged=stats.get("unchanged", 0),
        new=0, # Simplified
        deleted=0, # Simplified
    )


# ── Status Dashboard ──────────────────────────────────────────────────────────

@router.get("/status")
async def get_status(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_jwt),
):
    """
    Global and per-source refresh status.
    """
    result = await db.execute(
        select(SourceURL, RefreshStatus)
        .join(RefreshStatus, RefreshStatus.source_url_id == SourceURL.id, isouter=True)
        .where(SourceURL.is_active == True)
    )
    rows = result.all()

    per_source = []
    for source, rs in rows:
        per_source.append({
            "id": source.id,
            "url": source.url,
            "label": source.label,
            "source_type": source.source_type,
            "status": rs.current_status if rs else "pending",
            "last_attempt_at": rs.last_attempt_at if rs else None,
            "last_success_at": rs.last_success_at if rs else None,
            "error_message": rs.error_message if rs else None,
            "error_count": rs.error_count if rs else 0,
        })

    return {
        "total_sources": len(per_source),
        "refresh_in_progress": False, # Simplified, relies on background tasks
        "per_source": per_source,
    }
    
@router.get("/status/{url_id}")
async def get_status_detail(
    url_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_jwt),
):
    """Get detailed status for a single URL"""
    result = await db.execute(
        select(SourceURL, RefreshStatus)
        .join(RefreshStatus, RefreshStatus.source_url_id == SourceURL.id, isouter=True)
        .where(SourceURL.id == url_id)
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
        
    source, rs = row
    
    history_res = await db.execute(
        select(ScrapeHistory)
        .where(ScrapeHistory.source_url_id == url_id)
        .order_by(desc(ScrapeHistory.scraped_at))
        .limit(10)
    )
    history = history_res.scalars().all()
    
    return {
        "source": SourceURLResponse.model_validate(source),
        "status": rs.current_status if rs else "unknown",
        "last_attempt_at": rs.last_attempt_at if rs else None,
        "last_success_at": rs.last_success_at if rs else None,
        "error_message": rs.error_message if rs else None,
        "recent_history": [ScrapeHistoryResponse.model_validate(h) for h in history]
    }


@router.get("/history", response_model=list[ScrapeHistoryResponse])
async def get_history(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_jwt),
):
    """Paginated scrape history."""
    result = await db.execute(
        select(ScrapeHistory)
        .order_by(desc(ScrapeHistory.scraped_at))
        .offset(offset)
        .limit(limit)
    )
    return result.scalars().all()
    
@router.get("/errors", response_model=list[ScrapeHistoryResponse])
async def get_errors(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_jwt),
):
    """Recent scrape errors."""
    result = await db.execute(
        select(ScrapeHistory)
        .where(ScrapeHistory.status == "failed")
        .order_by(desc(ScrapeHistory.scraped_at))
        .limit(limit)
    )
    return result.scalars().all()

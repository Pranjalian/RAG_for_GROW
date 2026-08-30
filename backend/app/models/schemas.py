"""
Pydantic request/response schemas for the Groww Market Intelligence API.
All schemas are defined here as specified in implementation-plan §1.5.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, HttpUrl


# ── Source URLs ───────────────────────────────────────────────────────────────

class SourceURLCreate(BaseModel):
    url: str = Field(..., description="Full Groww URL to scrape")
    source_type: str = Field(
        ...,
        description="One of: mutual_fund | amc | nfo | market_news | filter",
    )
    label: Optional[str] = Field(None, description="Human-readable name for this source")


class SourceURLResponse(BaseModel):
    id: int
    url: str
    source_type: str
    label: Optional[str]
    is_active: bool
    added_by: Optional[str]
    added_at: datetime
    removed_at: Optional[datetime]

    model_config = {"from_attributes": True}


# ── Refresh Status ────────────────────────────────────────────────────────────

class RefreshStatusResponse(BaseModel):
    id: int
    source_url_id: int
    source_url: Optional[str] = None       # Joined from source_urls.url
    source_label: Optional[str] = None     # Joined from source_urls.label
    last_attempt_at: Optional[datetime]
    last_success_at: Optional[datetime]
    current_status: str
    content_hash: Optional[str]
    error_message: Optional[str]
    error_count: int
    updated_at: datetime

    model_config = {"from_attributes": True}


class GlobalRefreshStatusResponse(BaseModel):
    total_sources: int
    healthy_sources: int
    failed_sources: int
    stale_sources: int
    refresh_in_progress: bool
    last_global_refresh_at: Optional[datetime]
    next_scheduled_refresh_at: Optional[datetime]
    per_source: list[RefreshStatusResponse]


# ── Scrape History ────────────────────────────────────────────────────────────

class ScrapeHistoryResponse(BaseModel):
    id: int
    source_url_id: int
    scraped_at: datetime
    status: str
    content_hash: Optional[str]
    content_size: Optional[int]
    error_message: Optional[str]
    duration_ms: Optional[int]
    trigger_type: str

    model_config = {"from_attributes": True}


# ── Admin Auth ────────────────────────────────────────────────────────────────

class AdminLoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1, max_length=255)


class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int        # seconds


# ── Source Citations ──────────────────────────────────────────────────────────

class SourceCitation(BaseModel):
    source_url: str
    source_type: str
    source_label: Optional[str]
    last_refreshed: Optional[datetime]


# ── Chat ──────────────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    session_id: str = Field(..., description="Browser session UUID from localStorage")
    message: str = Field(..., min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    response: str
    query_type: str
    sources: list[SourceCitation]
    is_grounded: bool
    timestamp: datetime


class ChatStreamChunk(BaseModel):
    """Single chunk for WebSocket streaming responses."""
    type: str        # "text_chunk" | "source_citation" | "done" | "error"
    content: str
    metadata: Optional[dict[str, Any]] = None


# ── Comparison ────────────────────────────────────────────────────────────────

class ComparisonRequest(BaseModel):
    session_id: str
    fund_names: list[str] = Field(..., min_length=2, max_length=5)


class FundMetrics(BaseModel):
    """Factual metrics for one fund in a comparison."""
    fund_name: str
    nav: Optional[str]
    nav_date: Optional[str]
    returns_1y: Optional[str]
    returns_3y: Optional[str]
    returns_5y: Optional[str]
    expense_ratio: Optional[str]
    risk_level: Optional[str]
    fund_size_aum: Optional[str]
    rating: Optional[str]
    category: Optional[str]
    amc: Optional[str]
    source_url: Optional[str]
    last_refreshed: Optional[datetime]


class ComparisonResponse(BaseModel):
    funds: list[FundMetrics]
    sources: list[SourceCitation]
    note: str = "Factual comparison only. No investment recommendations."


# ── Watchlist ─────────────────────────────────────────────────────────────────

class WatchlistItemCreate(BaseModel):
    session_id: str
    item_type: str = Field(..., description="fund | amc | nfo_topic | news_topic")
    item_identifier: str
    label: Optional[str] = None


class WatchlistItemResponse(BaseModel):
    id: int
    session_id: str
    item_type: str
    item_identifier: str
    label: Optional[str]
    added_at: datetime

    model_config = {"from_attributes": True}


# ── Notification Preferences ──────────────────────────────────────────────────

class NotificationPrefsUpdate(BaseModel):
    session_id: str
    notify_new_nfo: bool = False
    notify_news: bool = False
    topics: Optional[list[str]] = None


class NotificationPrefsResponse(BaseModel):
    id: int
    session_id: str
    notify_new_nfo: bool
    notify_news: bool
    topics: Optional[list[str]]
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Notifications ─────────────────────────────────────────────────────────────

class NotificationItem(BaseModel):
    id: str
    type: str          # "new_nfo" | "new_news" | "fund_change"
    title: str
    body: str
    created_at: datetime
    read: bool = False


class NotificationsResponse(BaseModel):
    notifications: list[NotificationItem]


# ── Data Freshness ────────────────────────────────────────────────────────────

class FreshnessResponse(BaseModel):
    status: str           # "healthy" | "stale" | "failed" | "unavailable"
    total_sources: int
    healthy_count: int
    stale_count: int
    failed_count: int
    refresh_in_progress: bool
    last_refresh: Optional[datetime]


# ── Sync Trigger ──────────────────────────────────────────────────────────────

class SyncTriggerResponse(BaseModel):
    message: str
    trigger_type: str
    total: int
    success: int
    failed: int
    unchanged: int
    new: int
    deleted: int


# ── Health ────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    version: str = "0.1.0"
    database: str
    timestamp: datetime

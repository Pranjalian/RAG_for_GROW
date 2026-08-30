"""
All 9 SQLAlchemy ORM models corresponding to the PostgreSQL schema
defined in architecture §5.1.

Tables:
  1. admin_users
  2. source_urls
  3. refresh_status
  4. scrape_history
  5. nfo_tracking
  6. news_tracking
  7. watchlist_items
  8. notification_prefs
  9. system_state
"""

from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.db.session import Base


def _now() -> datetime:
    """UTC-aware current timestamp."""
    return datetime.now(timezone.utc)


# ── 1. admin_users ────────────────────────────────────────────────────────────

class AdminUser(Base):
    """
    Admin users table.
    Passwords are stored as bcrypt hashes — never plaintext.
    """
    __tablename__ = "admin_users"

    id            = Column(Integer, primary_key=True, index=True)
    username      = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at    = Column(DateTime(timezone=True), default=_now, nullable=False)


# ── 2. source_urls ────────────────────────────────────────────────────────────

class SourceURL(Base):
    """
    Configured scraping URLs — the authoritative list of sources.
    source_type enum: mutual_fund | amc | nfo | market_news | filter
    """
    __tablename__ = "source_urls"

    id          = Column(Integer, primary_key=True, index=True)
    url         = Column(Text, unique=True, nullable=False)
    source_type = Column(String(50), nullable=False)   # mutual_fund | amc | nfo | market_news | filter
    label       = Column(String(255), nullable=True)   # Human-readable name
    is_active   = Column(Boolean, default=True, nullable=False)
    added_by    = Column(String(100), nullable=True)
    added_at    = Column(DateTime(timezone=True), default=_now, nullable=False)
    removed_at  = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    refresh_status = relationship("RefreshStatus", back_populates="source_url", uselist=False,
                                  cascade="all, delete-orphan")
    scrape_history = relationship("ScrapeHistory", back_populates="source_url",
                                  cascade="all, delete-orphan")


# ── 3. refresh_status ─────────────────────────────────────────────────────────

class RefreshStatus(Base):
    """
    Per-source refresh tracking.
    current_status values: pending | scraping | success | failed | unchanged
    """
    __tablename__ = "refresh_status"

    id              = Column(Integer, primary_key=True, index=True)
    source_url_id   = Column(Integer, ForeignKey("source_urls.id", ondelete="CASCADE"), nullable=False)
    last_attempt_at = Column(DateTime(timezone=True), nullable=True)
    last_success_at = Column(DateTime(timezone=True), nullable=True)
    current_status  = Column(String(20), nullable=False, default="pending")
    content_hash    = Column(String(64), nullable=True)   # SHA-256 of last successful content
    error_message   = Column(Text, nullable=True)
    error_count     = Column(Integer, default=0, nullable=False)
    created_at      = Column(DateTime(timezone=True), default=_now, nullable=False)
    updated_at      = Column(DateTime(timezone=True), default=_now, onupdate=_now, nullable=False)

    source_url = relationship("SourceURL", back_populates="refresh_status")


# ── 4. scrape_history ─────────────────────────────────────────────────────────

class ScrapeHistory(Base):
    """
    Audit trail for every scrape attempt.
    status values: success | failed | unchanged
    trigger_type values: scheduler | admin_manual
    """
    __tablename__ = "scrape_history"

    id            = Column(Integer, primary_key=True, index=True)
    source_url_id = Column(Integer, ForeignKey("source_urls.id", ondelete="CASCADE"), nullable=False)
    scraped_at    = Column(DateTime(timezone=True), nullable=False)
    status        = Column(String(20), nullable=False)
    content_hash  = Column(String(64), nullable=True)
    content_size  = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    duration_ms   = Column(Integer, nullable=True)
    trigger_type  = Column(String(20), nullable=False)

    source_url = relationship("SourceURL", back_populates="scrape_history")


# ── 5. nfo_tracking ───────────────────────────────────────────────────────────

class NFOTracking(Base):
    """
    NFO change detection tracking.
    status values: open | closed | upcoming
    """
    __tablename__ = "nfo_tracking"

    id              = Column(Integer, primary_key=True, index=True)
    nfo_name        = Column(String(255), nullable=False)
    amc             = Column(String(255), nullable=True)
    category        = Column(String(100), nullable=True)
    status          = Column(String(50), nullable=True)    # open | closed | upcoming
    open_date       = Column(DateTime(timezone=True), nullable=True)
    close_date      = Column(DateTime(timezone=True), nullable=True)
    first_seen_at   = Column(DateTime(timezone=True), nullable=False)
    last_seen_at    = Column(DateTime(timezone=True), nullable=False)
    last_changed_at = Column(DateTime(timezone=True), nullable=True)
    content_hash    = Column(String(64), nullable=True)
    is_new          = Column(Boolean, default=True, nullable=False)
    notified        = Column(Boolean, default=False, nullable=False)


# ── 6. news_tracking ──────────────────────────────────────────────────────────

class NewsTracking(Base):
    """
    Market news change detection tracking.
    """
    __tablename__ = "news_tracking"

    id            = Column(Integer, primary_key=True, index=True)
    title         = Column(Text, nullable=False)
    source_url    = Column(Text, nullable=True)
    published_at  = Column(DateTime(timezone=True), nullable=True)
    summary       = Column(Text, nullable=True)
    first_seen_at = Column(DateTime(timezone=True), nullable=False)
    last_seen_at  = Column(DateTime(timezone=True), nullable=False)
    content_hash  = Column(String(64), nullable=True)
    is_new        = Column(Boolean, default=True, nullable=False)
    notified      = Column(Boolean, default=False, nullable=False)


# ── 7. watchlist_items ────────────────────────────────────────────────────────

class WatchlistItem(Base):
    """
    User watchlist — no login required, keyed by browser session UUID.
    item_type values: fund | amc | nfo_topic | news_topic
    """
    __tablename__ = "watchlist_items"

    id              = Column(Integer, primary_key=True, index=True)
    session_id      = Column(String(64), nullable=False, index=True)
    item_type       = Column(String(50), nullable=False)    # fund | amc | nfo_topic | news_topic
    item_identifier = Column(Text, nullable=False)          # fund URL, topic keyword, etc.
    label           = Column(String(255), nullable=True)
    added_at        = Column(DateTime(timezone=True), default=_now, nullable=False)


# ── 8. notification_prefs ─────────────────────────────────────────────────────

class NotificationPref(Base):
    """
    Per-session notification preferences.
    """
    __tablename__ = "notification_prefs"

    id             = Column(Integer, primary_key=True, index=True)
    session_id     = Column(String(64), nullable=False, index=True)
    notify_new_nfo = Column(Boolean, default=False, nullable=False)
    notify_news    = Column(Boolean, default=False, nullable=False)
    topics         = Column(JSON, nullable=True)   # keyword filters
    created_at     = Column(DateTime(timezone=True), default=_now, nullable=False)
    updated_at     = Column(DateTime(timezone=True), default=_now, onupdate=_now, nullable=False)


# ── 9. system_state ───────────────────────────────────────────────────────────

class SystemState(Base):
    """
    Global key-value system state.
    Keys: last_global_refresh_at | refresh_in_progress | total_sources | healthy_sources
    """
    __tablename__ = "system_state"

    key        = Column(String(100), primary_key=True)
    value      = Column(Text, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now, nullable=False)

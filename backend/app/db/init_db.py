"""
Database initialisation: create all tables and seed required data.

Called from FastAPI lifespan on application startup.
"""

import logging
from datetime import datetime, timezone

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.session import AsyncSessionLocal, Base, engine
from app.models.db_models import AdminUser, NotificationPref, NFOTracking  # noqa: F401
from app.models.db_models import NewsTracking, RefreshStatus, ScrapeHistory  # noqa: F401
from app.models.db_models import SourceURL, SystemState, WatchlistItem  # noqa: F401

logger = logging.getLogger(__name__)


# ── All 33 mandatory source URLs from problemStatement §3 ─────────────────────

MANDATORY_SOURCE_URLS: list[dict] = [
    # ── HDFC Funds (10) ──────────────────────────────────────────────────────
    {"url": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
     "source_type": "mutual_fund", "label": "HDFC Mid Cap Fund"},
    {"url": "https://groww.in/mutual-funds/hdfc-silver-etf-fof-direct-growth",
     "source_type": "mutual_fund", "label": "HDFC Silver ETF FoF"},
    {"url": "https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth",
     "source_type": "mutual_fund", "label": "HDFC Defence Fund"},
    {"url": "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth",
     "source_type": "mutual_fund", "label": "HDFC Equity Fund"},
    {"url": "https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth",
     "source_type": "mutual_fund", "label": "HDFC Gold ETF Fund of Fund"},
    {"url": "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
     "source_type": "mutual_fund", "label": "HDFC Small Cap Fund"},
    {"url": "https://groww.in/mutual-funds/hdfc-pharma-and-healthcare-fund-direct-growth",
     "source_type": "mutual_fund", "label": "HDFC Pharma and Healthcare Fund"},
    {"url": "https://groww.in/mutual-funds/hdfc-transportation-and-logistics-fund-direct-growth",
     "source_type": "mutual_fund", "label": "HDFC Transportation and Logistics Fund"},
    {"url": "https://groww.in/mutual-funds/hdfc-large-and-mid-cap-fund-direct-growth",
     "source_type": "mutual_fund", "label": "HDFC Large and Mid Cap Fund"},
    {"url": "https://groww.in/mutual-funds/hdfc-nifty-next-50-index-fund-direct-growth",
     "source_type": "mutual_fund", "label": "HDFC Nifty Next 50 Index Fund"},
    # ── Groww Funds (4) ───────────────────────────────────────────────────────
    {"url": "https://groww.in/mutual-funds/groww-banking-financial-services-fund-direct-growth",
     "source_type": "mutual_fund", "label": "Groww Banking & Financial Services Fund"},
    {"url": "https://groww.in/mutual-funds/groww-nifty-ev-new-age-automotive-etf-fof-direct-growth",
     "source_type": "mutual_fund", "label": "Groww Nifty EV & New Age Automotive ETF FoF"},
    {"url": "https://groww.in/mutual-funds/groww-nifty-india-defence-etf-fof-direct-growth",
     "source_type": "mutual_fund", "label": "Groww Nifty India Defence ETF FoF"},
    {"url": "https://groww.in/mutual-funds/groww-multicap-fund-direct-growth",
     "source_type": "mutual_fund", "label": "Groww Multicap Fund"},
    # ── Nippon India Funds (4) ────────────────────────────────────────────────
    {"url": "https://groww.in/mutual-funds/nippon-india-small-cap-fund-direct-growth",
     "source_type": "mutual_fund", "label": "Nippon India Small Cap Fund"},
    {"url": "https://groww.in/mutual-funds/nippon-india-large-cap-fund-direct-growth",
     "source_type": "mutual_fund", "label": "Nippon India Large Cap Fund"},
    {"url": "https://groww.in/mutual-funds/nippon-india-nifty-midcap-150-index-fund-direct-growth",
     "source_type": "mutual_fund", "label": "Nippon India Nifty Midcap 150 Index Fund"},
    {"url": "https://groww.in/mutual-funds/nippon-india-pharma-fund-direct-growth",
     "source_type": "mutual_fund", "label": "Nippon India Pharma Fund"},
    # ── Aditya Birla AMC Page (1) ─────────────────────────────────────────────
    {"url": "https://groww.in/mutual-funds/amc/aditya-birla-sun-life-mutual-funds",
     "source_type": "amc", "label": "Aditya Birla Sun Life Mutual Fund — AMC Page"},
    # ── Aditya Birla / Birla Funds (9) ────────────────────────────────────────
    {"url": "https://groww.in/mutual-funds/birla-sun-life-manufacturing-equity-fund-direct-growth",
     "source_type": "mutual_fund", "label": "Birla Sun Life Manufacturing Equity Fund"},
    {"url": "https://groww.in/mutual-funds/aditya-birla-sun-life-psu-equity-fund-direct-growth",
     "source_type": "mutual_fund", "label": "Aditya Birla Sun Life PSU Equity Fund"},
    {"url": "https://groww.in/mutual-funds/aditya-birla-sun-life-nifty-india-defence-index-fund-direct-growth",
     "source_type": "mutual_fund", "label": "Aditya Birla Sun Life Nifty India Defence Index Fund"},
    {"url": "https://groww.in/mutual-funds/birla-sun-life-corporate-bond-fund-direct-growth",
     "source_type": "mutual_fund", "label": "Birla Sun Life Corporate Bond Fund"},
    {"url": "https://groww.in/mutual-funds/birla-sun-life-equity-fund-direct-growth",
     "source_type": "mutual_fund", "label": "Birla Sun Life Equity Fund"},
    {"url": "https://groww.in/mutual-funds/aditya-birla-sun-life-pharma-healthcare-fund-direct-growth",
     "source_type": "mutual_fund", "label": "Aditya Birla Sun Life Pharma & Healthcare Fund"},
    {"url": "https://groww.in/mutual-funds/aditya-birla-sun-life-transportation-and-logistics-fund-direct-growth",
     "source_type": "mutual_fund", "label": "Aditya Birla Sun Life Transportation & Logistics Fund"},
    {"url": "https://groww.in/mutual-funds/aditya-birla-sun-life-multi-asset-allocation-fund-direct-growth",
     "source_type": "mutual_fund", "label": "Aditya Birla Sun Life Multi Asset Allocation Fund"},
    # ── Franklin Funds (3) ────────────────────────────────────────────────────
    {"url": "https://groww.in/mutual-funds/franklin-india-small-cap-fund-direct-growth",
     "source_type": "mutual_fund", "label": "Franklin India Small Cap Fund"},
    {"url": "https://groww.in/mutual-funds/franklin-india-multi-cap-fund-direct-growth",
     "source_type": "mutual_fund", "label": "Franklin India Multi Cap Fund"},
    {"url": "https://groww.in/mutual-funds/franklin-india-multi-asset-allocation-fund-direct-growth",
     "source_type": "mutual_fund", "label": "Franklin India Multi Asset Allocation Fund"},
    # ── Filter Page (1) ───────────────────────────────────────────────────────
    {
        "url": (
            "https://groww.in/mutual-funds/filter?fund_house=%5B%22Nippon+India+Mutual+Fund%22%2C"
            "%22Aditya+Birla+Sun+Life+Mutual+Fund%22%2C%22Angel+One+Mutual+Fund%22%2C%22Axis+Mutual"
            "+Fund%22%2C%22Bajaj+Finserv+Mutual+Fund%22%2C%22Franklin+Templeton+Mutual+Fund%22%2C"
            "%22Groww+Mutual+Fund%22%2C%22HDFC+Mutual+Fund%22%2C%22HSBC+Mutual+Fund%22%2C%22ICICI"
            "+Prudential+Mutual+Fund%22%2C%22IDFC+Mutual+Fund%22%2C%22IIFL+Mutual+Fund%22%2C"
            "%22Kotak+Mahindra+Mutual+Fund%22%2C%22LIC+Mutual+Fund%22%2C%22Motilal+Oswal+Mutual"
            "+Fund%22%2C%22Navi+Mutual+Fund%22%2C%22Quantum+Mutual+Fund%22%2C%22SBI+Mutual+Fund"
            "%22%2C%22Tata+Mutual+Fund%22%2C%22Zerodha+Mutual+Fund%22%2C%22YES+Mutual+Fund%22%5D"
        ),
        "source_type": "filter",
        "label": "Fund House Filter — Multi-AMC Listing",
    },
    # ── Market News (1) ───────────────────────────────────────────────────────
    {"url": "https://groww.in/share-market-today",
     "source_type": "market_news", "label": "Share Market Today — Market News"},
    # ── NFO (1) ───────────────────────────────────────────────────────────────
    {"url": "https://groww.in/nfo",
     "source_type": "nfo", "label": "New Fund Offerings (NFO)"},
]


async def init_database() -> None:
    """Create all tables if they don't exist (idempotent)."""
    logger.info("Initialising database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables ready.")


async def seed_admin_user() -> None:
    """
    Seed the default admin user if it does not already exist.
    Password is bcrypt-hashed. Idempotent (uses INSERT ... ON CONFLICT DO NOTHING).
    """
    from app.auth.password import hash_password  # local import to avoid circular deps

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(AdminUser).where(AdminUser.username == settings.ADMIN_DEFAULT_USERNAME)
        )
        existing = result.scalar_one_or_none()
        if existing:
            logger.info("Admin user '%s' already exists — skipping seed.", settings.ADMIN_DEFAULT_USERNAME)
            return

        admin = AdminUser(
            username=settings.ADMIN_DEFAULT_USERNAME,
            password_hash=hash_password(settings.ADMIN_DEFAULT_PASSWORD),
        )
        db.add(admin)
        await db.commit()
        logger.info("Seeded admin user '%s'.", settings.ADMIN_DEFAULT_USERNAME)


async def seed_initial_urls() -> None:
    """
    Seed all 33 mandatory source URLs if they don't already exist.
    For each new URL, also creates an initial refresh_status row (status=pending).
    Idempotent — skips URLs that already exist.
    """
    async with AsyncSessionLocal() as db:
        newly_added = 0
        for entry in MANDATORY_SOURCE_URLS:
            result = await db.execute(
                select(SourceURL).where(SourceURL.url == entry["url"])
            )
            existing = result.scalar_one_or_none()
            if existing:
                continue

            source = SourceURL(
                url=entry["url"],
                source_type=entry["source_type"],
                label=entry.get("label"),
                is_active=True,
                added_by="system_seed",
            )
            db.add(source)
            await db.flush()  # Get the generated source.id

            status = RefreshStatus(
                source_url_id=source.id,
                current_status="pending",
            )
            db.add(status)
            newly_added += 1

        await db.commit()

        if newly_added:
            logger.info("Seeded %d mandatory source URLs.", newly_added)
        else:
            logger.info("All mandatory source URLs already present — skipping seed.")


async def seed_system_state() -> None:
    """
    Seed initial system_state key-value rows.
    Idempotent — skips keys that already exist.
    """
    initial_state = {
        "last_global_refresh_at": "",
        "refresh_in_progress": "false",
        "total_sources": "0",
        "healthy_sources": "0",
    }

    async with AsyncSessionLocal() as db:
        for key, value in initial_state.items():
            result = await db.execute(
                select(SystemState).where(SystemState.key == key)
            )
            existing = result.scalar_one_or_none()
            if not existing:
                db.add(SystemState(key=key, value=value))

        await db.commit()
        logger.info("System state initialised.")

"""
FastAPI application factory with lifespan, middleware, and route registration.
Architecture reference: §1.4, §14.2.
"""

import logging
import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import settings
from app.db.init_db import init_database, seed_admin_user, seed_initial_urls, seed_system_state
from app.models.schemas import HealthResponse

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ── Rate Limiter ──────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup/shutdown lifecycle.

    Startup sequence (architecture §1.4):
      1. Create all DB tables
      2. Seed admin user (idempotent)
      3. Seed all 33 mandatory source URLs (idempotent)
      4. Seed system state key-value rows (idempotent)
      5. Initialize Scraper Engine
      6. Start APScheduler
    """
    logger.info("=== Groww Market Intelligence RAG — Starting Up ===")

    await init_database()
    await seed_admin_user()
    await seed_initial_urls()
    await seed_system_state()
    
    from app.scraper.engine import scraper_engine
    await scraper_engine.initialize()
    
    from app.pipeline.scheduler import start_scheduler, scheduler
    start_scheduler()

    # Initial data load if needed can be triggered here as a background task
    # asyncio.create_task(sync_engine.run_sync_cycle("startup"))

    logger.info("=== Startup complete. Backend is ready. ===")
    yield
    # ── Shutdown ──────────────────────────────────────────────────────────────
    logger.info("=== Shutting down. ===")
    scheduler.shutdown(wait=False)
    await scraper_engine.shutdown()


# ── App factory ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="Groww Market Intelligence RAG",
    description=(
        "Source-grounded RAG chatbot for Groww mutual fund, NFO, and market news data. "
        "Powered by GROK LLM. Strictly factual — no investment advice."
    ),
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Middleware ─────────────────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
from app.api import admin, chat, data  # noqa: E402 — after app creation to avoid circular imports

app.include_router(chat.router,  prefix="/api/chat",  tags=["Chat"])
app.include_router(data.router,  prefix="/api/data",  tags=["Data"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])


# ── Health Check ──────────────────────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    Returns 200 OK when the backend is running and the database is reachable.
    Used by Docker Compose healthcheck and monitoring.
    """
    from app.db.session import engine
    db_status = "unknown"
    try:
        async with engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        db_status = "healthy"
    except Exception as exc:
        logger.warning("Health check DB ping failed: %s", exc)
        db_status = "unreachable"

    return HealthResponse(
        status="healthy",
        database=db_status,
        timestamp=datetime.now(timezone.utc),
    )


@app.get("/", tags=["System"])
async def root():
    """Root redirect — points to API docs."""
    return {"message": "Groww Market Intelligence RAG API", "docs": "/docs", "health": "/health"}

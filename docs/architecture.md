# Groww Market Intelligence — System Architecture

## Table of Contents
1. [Architecture Overview](#1-architecture-overview)
2. [High-Level System Diagram](#2-high-level-system-diagram)
3. [Technology Stack](#3-technology-stack)
4. [Layer-by-Layer Architecture](#4-layer-by-layer-architecture)
5. [Data Models & Schemas](#5-data-models--schemas)
6. [API Design](#6-api-design)
7. [Scraping & Ingestion Pipeline](#7-scraping--ingestion-pipeline)
8. [Vector Database Synchronization Engine](#8-vector-database-synchronization-engine)
9. [RAG Query Pipeline](#9-rag-query-pipeline)
10. [Conversation Management](#10-conversation-management)
11. [Admin Subsystem](#11-admin-subsystem)
12. [Notification Subsystem](#12-notification-subsystem)
13. [Frontend Architecture](#13-frontend-architecture)
14. [Security Architecture](#14-security-architecture)
15. [Deployment Architecture](#15-deployment-architecture)
16. [Error Handling & Resilience](#16-error-handling--resilience)
17. [Directory Structure](#17-directory-structure)

---

## 1. Architecture Overview

The system is a **source-grounded RAG chatbot** built on a five-layer architecture:

| Layer | Responsibility |
|---|---|
| **Presentation** | React frontend — chat UI, admin panel, comparison workspace, NFO/news sections |
| **API Gateway** | FastAPI backend — REST endpoints, WebSocket for chat, JWT auth for admin |
| **RAG Engine** | LangChain orchestration — query classification, retrieval, grounded generation |
| **Data Pipeline** | APScheduler + Playwright/Scrapy — 15-min scraping, change detection, embedding |
| **Persistence** | ChromaDB (vectors), PostgreSQL (metadata, admin state, URL config, refresh logs) |

### Core Design Principles

```
┌────────────────────────────────────────────────────────────┐
│                    DESIGN PRINCIPLES                       │
├────────────────────────────────────────────────────────────┤
│ 1. SOURCE-GROUNDED   → Every answer from Groww data only  │
│ 2. INCREMENTAL SYNC  → Per-source change detection        │
│ 3. FAIL-SAFE         → Failed scrape ≠ data loss          │
│ 4. NO ADVICE         → Strict system prompt enforcement   │
│ 5. TRANSPARENT       → Source + timestamp in every answer │
│ 6. SEPARATION        → User chat ≠ Admin operations       │
└────────────────────────────────────────────────────────────┘
```

---

## 2. High-Level System Diagram

```mermaid
graph TB
    subgraph "Presentation Layer"
        UI["React Frontend"]
        CHAT_UI["Chat Interface"]
        ADMIN_UI["Admin Panel"]
        COMP_UI["Comparison Workspace"]
        NFO_UI["NFO Discovery"]
        NEWS_UI["Market News Feed"]
        WATCH_UI["Watchlist"]
    end

    subgraph "API Layer — FastAPI"
        GW["API Gateway"]
        AUTH["JWT Auth Middleware"]
        CHAT_API["Chat API (WebSocket)"]
        ADMIN_API["Admin API (REST)"]
        DATA_API["Data API (REST)"]
        NOTIFY_API["Notification API"]
    end

    subgraph "RAG Engine — LangChain"
        QC["Query Classifier"]
        RET["Retriever"]
        GEN["Grounded Generator"]
        CONV["Conversation Memory"]
        GUARD["Guardrail / Grounding Filter"]
    end

    subgraph "Data Pipeline"
        SCHED["APScheduler (15-min)"]
        SCRAPER["Scraper Engine (Playwright)"]
        PARSER["Content Parser & Normalizer"]
        DIFF["Change Detector (Diffing)"]
        EMBED["Embedding Pipeline"]
        SYNC["Vector Sync Engine"]
    end

    subgraph "Persistence Layer"
        PG["PostgreSQL"]
        CHROMA["ChromaDB"]
        SNAP["Snapshot Store (JSON on disk)"]
    end

    UI --> GW
    CHAT_UI --> CHAT_API
    ADMIN_UI --> AUTH --> ADMIN_API
    COMP_UI --> DATA_API
    NFO_UI --> DATA_API
    NEWS_UI --> DATA_API
    WATCH_UI --> DATA_API

    CHAT_API --> QC --> RET --> CHROMA
    RET --> GEN --> GUARD
    GEN --> CONV

    ADMIN_API --> PG
    ADMIN_API --> SCHED

    SCHED --> SCRAPER --> PARSER --> DIFF --> EMBED --> SYNC --> CHROMA
    DIFF --> PG
    DIFF --> SNAP
    SYNC --> PG

    NOTIFY_API --> PG
```

---

## 3. Technology Stack

### Backend

| Component | Technology | Rationale |
|---|---|---|
| **Web Framework** | FastAPI (Python 3.11+) | Async support, WebSocket native, OpenAPI auto-docs |
| **Task Scheduler** | APScheduler | In-process 15-min cron, admin-triggerable |
| **Web Scraper** | Playwright (async) | Handles JS-rendered Groww pages, headless Chromium |
| **HTML Parser** | BeautifulSoup4 + custom extractors | Structured field extraction per page type |
| **Embedding Model** | `sentence-transformers/all-MiniLM-L6-v2` (384-dim) | Fast, good quality, runs locally |
| **Vector Store** | ChromaDB (persistent mode) | Simple setup, metadata filtering, local persistence |
| **LLM** | GROK LLM | High performance, excellent reasoning capabilities |
| **RAG Orchestration** | LangChain | Retriever chains, conversation memory, prompt templates |
| **Relational DB** | PostgreSQL 15 (or SQLite for dev) | URL config, refresh logs, user watchlists, admin state |
| **ORM** | SQLAlchemy 2.0 + Alembic | Async ORM, schema migrations |
| **Auth** | PyJWT + bcrypt | Admin JWT tokens, password hashing |

### Frontend

| Component | Technology | Rationale |
|---|---|---|
| **Framework** | React 18 + Vite | Fast dev, component model |
| **Styling** | Vanilla CSS + CSS Variables | Full control, design-system tokens |
| **HTTP Client** | Axios | Interceptors for JWT |
| **WebSocket** | Native WebSocket API | Real-time chat streaming |
| **State Management** | React Context + useReducer | Sufficient for this scope |
| **Charting** | Recharts | Fund comparison charts |

---

## 4. Layer-by-Layer Architecture

### 4.1 Presentation Layer

```mermaid
graph LR
    subgraph "React App"
        direction TB
        APP["App Shell"]
        APP --> ROUTER["React Router"]
        ROUTER --> CHAT_PAGE["/ — Chat Page"]
        ROUTER --> COMPARE_PAGE["/compare — Comparison"]
        ROUTER --> NFO_PAGE["/nfo — NFO Discovery"]
        ROUTER --> NEWS_PAGE["/news — Market News"]
        ROUTER --> WATCHLIST_PAGE["/watchlist — Watchlist"]
        ROUTER --> ADMIN_LOGIN["/admin/login — Admin Login"]
        ROUTER --> ADMIN_DASH["/admin/dashboard — Admin Dashboard"]
    end
```

**Key UI Components:**

| Component | Description |
|---|---|
| `ChatWindow` | Message list + streaming response display |
| `ChatInput` | User query input with send button |
| `SourceBadge` | Shows source type (MF/AMC/NFO/News) + refresh timestamp |
| `FreshnessIndicator` | Global data-availability status bar (green/amber/red) |
| `SourceOnlyBanner` | Persistent "Groww Source-Only Mode" indicator |
| `ComparisonTable` | Side-by-side fund metric table with "N/A" for missing fields |
| `NFOCard` | NFO listing with status, dates, AMC, "NEW" badge |
| `NewsCard` | Market news item with title, time, summary |
| `WatchlistPanel` | Saved funds/topics with change indicators |
| `AdminURLManager` | CRUD table for scraping URLs |
| `AdminRefreshStatus` | Per-source status dashboard with error logs |

### 4.2 API Gateway Layer

The FastAPI application exposes three route groups:

```
/api/chat/*          → Public (no auth) — WebSocket chat, conversation history
/api/data/*          → Public (no auth) — Fund list, NFOs, news, comparisons, watchlist
/api/admin/*         → Protected (JWT)  — URL CRUD, trigger refresh, view status
```

### 4.3 RAG Engine Layer

```mermaid
graph LR
    Q["User Query"] --> CLASSIFY["Query Classifier"]
    CLASSIFY -->|fund_lookup| R1["Fund Retriever"]
    CLASSIFY -->|comparison| R2["Comparison Retriever"]
    CLASSIFY -->|nfo_query| R3["NFO Retriever"]
    CLASSIFY -->|news_query| R4["News Retriever"]
    CLASSIFY -->|freshness| R5["Metadata Retriever"]
    CLASSIFY -->|change_query| R6["Change Diff Retriever"]
    CLASSIFY -->|advice_request| BLOCK["Advice Blocker"]

    R1 & R2 & R3 & R4 & R5 & R6 --> MERGE["Context Merger"]
    MERGE --> PROMPT["Grounded Prompt Builder"]
    PROMPT --> LLM["GROK LLM"]
    LLM --> GUARD["Grounding Guardrail"]
    GUARD -->|pass| RESP["Response + Source Citations"]
    GUARD -->|fail| FALLBACK["'Currently I dont have the data to answer the query'"]
    BLOCK --> DECLINE["Informational-only decline response"]
```

### 4.4 Data Pipeline Layer

```mermaid
graph LR
    TRIGGER["Trigger (Scheduler / Admin)"] --> FETCH["Fetch URL List from DB"]
    FETCH --> LOOP["For each URL"]
    LOOP --> SCRAPE["Playwright Scrape"]
    SCRAPE -->|success| PARSE["Parse & Extract Fields"]
    SCRAPE -->|failure| LOG_FAIL["Record Failure in DB"]
    PARSE --> HASH["Content Hash (SHA-256)"]
    HASH -->|unchanged| SKIP["Skip — retain vectors"]
    HASH -->|changed| DIFF_STORE["Store Diff Snapshot"]
    DIFF_STORE --> CHUNK["Chunk Content"]
    CHUNK --> EMBED_VEC["Generate Embeddings"]
    EMBED_VEC --> UPSERT["Upsert to ChromaDB (delete old + insert new for this source)"]
    UPSERT --> UPDATE_META["Update refresh metadata in PostgreSQL"]
    LOG_FAIL --> RETAIN["Retain previous vectors — no deletion"]
```

### 4.5 Persistence Layer

```
PostgreSQL                          ChromaDB                      Disk
┌──────────────────────┐    ┌──────────────────────────┐    ┌────────────────────┐
│ source_urls          │    │ Collection: groww_funds   │    │ snapshots/         │
│ scrape_history       │    │   - doc chunks            │    │   {url_hash}/      │
│ refresh_status       │    │   - embeddings (384-dim)  │    │     current.json   │
│ admin_users          │    │   - metadata filters:     │    │     previous.json  │
│ user_sessions        │    │     source_url            │    │     diff.json      │
│ watchlist_items      │    │     source_type           │    └────────────────────┘
│ notification_prefs   │    │     fund_name             │
│ nfo_tracking         │    │     scraped_at            │
│ news_tracking        │    │     content_hash          │
└──────────────────────┘    └──────────────────────────┘
```

---

## 5. Data Models & Schemas

### 5.1 PostgreSQL Tables

```sql
-- Admin users (bcrypt-hashed passwords)
CREATE TABLE admin_users (
    id              SERIAL PRIMARY KEY,
    username        VARCHAR(100) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Configured scraping URLs (authoritative source list)
CREATE TABLE source_urls (
    id              SERIAL PRIMARY KEY,
    url             TEXT UNIQUE NOT NULL,
    source_type     VARCHAR(50) NOT NULL,  -- 'mutual_fund', 'amc', 'nfo', 'market_news', 'filter'
    label           VARCHAR(255),           -- Human-readable name
    is_active       BOOLEAN DEFAULT TRUE,
    added_by        VARCHAR(100),
    added_at        TIMESTAMP DEFAULT NOW(),
    removed_at      TIMESTAMP
);
-- source_type enum: mutual_fund | amc | nfo | market_news | filter

-- Per-source refresh tracking
CREATE TABLE refresh_status (
    id                      SERIAL PRIMARY KEY,
    source_url_id           INTEGER REFERENCES source_urls(id) ON DELETE CASCADE,
    last_attempt_at         TIMESTAMP,
    last_success_at         TIMESTAMP,
    current_status          VARCHAR(20) NOT NULL DEFAULT 'pending',
    -- 'pending', 'scraping', 'success', 'failed', 'unchanged'
    content_hash            VARCHAR(64),       -- SHA-256 of last successful content
    error_message           TEXT,
    error_count             INTEGER DEFAULT 0,
    created_at              TIMESTAMP DEFAULT NOW(),
    updated_at              TIMESTAMP DEFAULT NOW()
);

-- Scrape history log (audit trail)
CREATE TABLE scrape_history (
    id              SERIAL PRIMARY KEY,
    source_url_id   INTEGER REFERENCES source_urls(id) ON DELETE CASCADE,
    scraped_at      TIMESTAMP NOT NULL,
    status          VARCHAR(20) NOT NULL,   -- 'success', 'failed', 'unchanged'
    content_hash    VARCHAR(64),
    content_size    INTEGER,
    error_message   TEXT,
    duration_ms     INTEGER,
    trigger_type    VARCHAR(20) NOT NULL     -- 'scheduler', 'admin_manual'
);

-- NFO tracking for change detection
CREATE TABLE nfo_tracking (
    id              SERIAL PRIMARY KEY,
    nfo_name        VARCHAR(255) NOT NULL,
    amc             VARCHAR(255),
    category        VARCHAR(100),
    status          VARCHAR(50),            -- 'open', 'closed', 'upcoming'
    open_date       DATE,
    close_date      DATE,
    first_seen_at   TIMESTAMP NOT NULL,
    last_seen_at    TIMESTAMP NOT NULL,
    last_changed_at TIMESTAMP,
    content_hash    VARCHAR(64),
    is_new          BOOLEAN DEFAULT TRUE,
    notified        BOOLEAN DEFAULT FALSE
);

-- Market news tracking for change detection
CREATE TABLE news_tracking (
    id              SERIAL PRIMARY KEY,
    title           TEXT NOT NULL,
    source_url      TEXT,
    published_at    TIMESTAMP,
    summary         TEXT,
    first_seen_at   TIMESTAMP NOT NULL,
    last_seen_at    TIMESTAMP NOT NULL,
    content_hash    VARCHAR(64),
    is_new          BOOLEAN DEFAULT TRUE,
    notified        BOOLEAN DEFAULT FALSE
);

-- User watchlist (no login — uses session/localStorage ID)
CREATE TABLE watchlist_items (
    id              SERIAL PRIMARY KEY,
    session_id      VARCHAR(64) NOT NULL,
    item_type       VARCHAR(50) NOT NULL,   -- 'fund', 'amc', 'nfo_topic', 'news_topic'
    item_identifier TEXT NOT NULL,           -- fund URL, topic keyword, etc.
    label           VARCHAR(255),
    added_at        TIMESTAMP DEFAULT NOW()
);

-- Notification preferences
CREATE TABLE notification_prefs (
    id              SERIAL PRIMARY KEY,
    session_id      VARCHAR(64) NOT NULL,
    notify_new_nfo  BOOLEAN DEFAULT FALSE,
    notify_news     BOOLEAN DEFAULT FALSE,
    topics          TEXT[],                  -- keyword filters
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

-- Global system state
CREATE TABLE system_state (
    key             VARCHAR(100) PRIMARY KEY,
    value           TEXT NOT NULL,
    updated_at      TIMESTAMP DEFAULT NOW()
);
-- Keys: 'last_global_refresh_at', 'refresh_in_progress', 'total_sources', 'healthy_sources'
```

### 5.2 ChromaDB Document Schema

Each document chunk stored in ChromaDB carries this metadata:

```python
{
    "id":             "sha256({source_url}:{chunk_index}:{content_hash})",
    "document":       "...chunk text...",
    "embedding":      [0.012, -0.045, ...],  # 384-dim float32
    "metadata": {
        "source_url":       "https://groww.in/mutual-funds/...",
        "source_type":      "mutual_fund",       # mutual_fund | amc | nfo | market_news | filter
        "fund_name":        "HDFC Mid Cap Fund",  # null for news/nfo
        "amc":              "HDFC Mutual Fund",
        "category":         "Mid Cap",
        "content_hash":     "a1b2c3...",
        "scraped_at":       "2026-08-25T13:30:00+05:30",
        "chunk_index":      0,
        "total_chunks":     5,
        "section":          "overview",          # overview | returns | holdings | news | nfo
    }
}
```

### 5.3 Snapshot File Structure

```json
// snapshots/{url_sha256}/current.json
{
    "source_url": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
    "source_type": "mutual_fund",
    "scraped_at": "2026-08-25T13:30:00+05:30",
    "content_hash": "a1b2c3d4...",
    "extracted_data": {
        "fund_name": "HDFC Mid Cap Fund",
        "nav": "835.42",
        "nav_date": "2026-08-22",
        "expense_ratio": "1.04%",
        "returns_1y": "32.5%",
        "returns_3y": "22.1%",
        "returns_5y": "18.7%",
        "risk_level": "Very High",
        "fund_size": "₹56,789 Cr",
        "exit_load": "1% if redeemed within 1 year",
        "fund_manager": "Chirag Setalvad",
        "category": "Mid Cap",
        "amc": "HDFC Mutual Fund",
        "benchmark": "NIFTY Midcap 150 TRI",
        "rating": "5 star"
    },
    "raw_text_sections": {
        "overview": "...",
        "returns": "...",
        "holdings": "...",
        "peer_comparison": "..."
    }
}
```

```json
// snapshots/{url_sha256}/diff.json
{
    "compared_at": "2026-08-25T13:30:00+05:30",
    "previous_hash": "x9y8z7...",
    "current_hash": "a1b2c3d4...",
    "changes": [
        {"field": "nav", "old": "832.10", "new": "835.42"},
        {"field": "returns_1y", "old": "31.8%", "new": "32.5%"}
    ]
}
```

---

## 6. API Design

### 6.1 Public Chat API (WebSocket)

```
WS /api/chat/ws?session_id={session_id}
```

**Client → Server message:**
```json
{
    "type": "user_message",
    "content": "What is the NAV of HDFC Mid Cap Fund?",
    "conversation_id": "conv_abc123"
}
```

**Server → Client message (streamed):**
```json
{
    "type": "assistant_chunk",
    "content": "The current NAV of HDFC Mid Cap Fund is ",
    "done": false
}
```

**Server → Client message (final):**
```json
{
    "type": "assistant_message",
    "content": "The current NAV of HDFC Mid Cap Fund is ₹835.42 as of 22 Aug 2026.",
    "sources": [
        {
            "source_url": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
            "source_type": "mutual_fund",
            "last_refreshed": "2026-08-25T13:30:00+05:30"
        }
    ],
    "done": true
}
```

### 6.2 Public Data API (REST)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/data/funds` | List all collected funds with basic metadata |
| GET | `/api/data/funds/{fund_slug}` | Get latest extracted data for one fund |
| POST | `/api/data/compare` | Compare multiple funds (body: `{ "fund_slugs": [...] }`) |
| GET | `/api/data/nfo` | List all tracked NFOs with status |
| GET | `/api/data/nfo/new` | List NFOs detected as new since last refresh |
| GET | `/api/data/news` | List latest market news items |
| GET | `/api/data/news/new` | List news items detected as new since last refresh |
| GET | `/api/data/changes?source_url={url}` | Get detected changes for a source since previous refresh |
| GET | `/api/data/freshness` | Global and per-source freshness status |
| GET | `/api/data/watchlist?session_id={id}` | Get user's saved watchlist items |
| POST | `/api/data/watchlist` | Add item to watchlist |
| DELETE | `/api/data/watchlist/{item_id}` | Remove item from watchlist |
| GET | `/api/data/notifications?session_id={id}` | Get pending notifications for user |
| POST | `/api/data/notifications/prefs` | Save notification preferences |

### 6.3 Admin API (JWT-Protected REST)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/admin/login` | Authenticate → returns JWT |
| GET | `/api/admin/urls` | List all configured source URLs |
| POST | `/api/admin/urls` | Add a new source URL |
| DELETE | `/api/admin/urls/{id}` | Remove a source URL |
| PUT | `/api/admin/urls/{id}` | Update a source URL |
| POST | `/api/admin/sync` | Manually trigger scrape + sync cycle |
| GET | `/api/admin/status` | Global refresh status summary |
| GET | `/api/admin/status/{source_url_id}` | Per-source detailed status |
| GET | `/api/admin/history` | Scrape history log with filters |
| GET | `/api/admin/errors` | Recent scraping errors |

**Login Request/Response:**
```json
// POST /api/admin/login
// Request:
{ "username": "admin", "password": "admin" }

// Response (200):
{
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 3600
}
```

---

## 7. Scraping & Ingestion Pipeline

### 7.1 Scraper Engine Design

```mermaid
graph TB
    subgraph "Scraper Engine"
        INIT["Initialize Playwright Browser (Chromium headless)"]
        INIT --> POOL["Browser Context Pool (max 5 concurrent)"]
        POOL --> ROUTE{"URL Type Router"}

        ROUTE -->|mutual_fund| MF_SCRAPER["MutualFundScraper"]
        ROUTE -->|amc| AMC_SCRAPER["AMCScraper"]
        ROUTE -->|nfo| NFO_SCRAPER["NFOScraper"]
        ROUTE -->|market_news| NEWS_SCRAPER["MarketNewsScraper"]
        ROUTE -->|filter| FILTER_SCRAPER["FilterPageScraper"]

        MF_SCRAPER --> EXTRACT["Field Extractor"]
        AMC_SCRAPER --> EXTRACT
        NFO_SCRAPER --> EXTRACT
        NEWS_SCRAPER --> EXTRACT
        FILTER_SCRAPER --> EXTRACT

        EXTRACT --> VALIDATE["Data Validator"]
        VALIDATE --> NORMALIZE["Normalizer"]
    end
```

### 7.2 Page-Type Specific Extractors

```python
# Mutual Fund page fields to extract
MUTUAL_FUND_FIELDS = [
    "fund_name", "nav", "nav_date", "returns_1y", "returns_3y",
    "returns_5y", "returns_7y", "returns_10y", "expense_ratio",
    "exit_load", "risk_level", "fund_size_aum", "rating",
    "fund_manager", "category", "sub_category", "amc",
    "benchmark", "scheme_type", "plan", "investment_objective",
    "top_holdings",         # list of {name, percentage}
    "sector_allocation",    # list of {sector, percentage}
    "asset_allocation",     # {equity, debt, cash, other}
]

# NFO page fields to extract
NFO_FIELDS = [
    "nfo_name", "amc", "category", "sub_category",
    "subscription_status", "open_date", "close_date",
    "scheme_type", "min_investment", "benchmark",
]

# Market News fields to extract
NEWS_FIELDS = [
    "title", "summary", "published_at", "updated_at",
    "category", "tags", "article_url",
]
```

### 7.3 Content Hashing Strategy

```python
def compute_content_hash(extracted_data: dict) -> str:
    """
    Deterministic SHA-256 hash of normalized extracted content.
    Used to detect changes between scrape cycles.
    """
    # Sort keys for deterministic serialization
    canonical = json.dumps(extracted_data, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
```

### 7.4 Chunking Strategy

```python
CHUNKING_CONFIG = {
    "mutual_fund": {
        "strategy": "single_document_textification",
        "max_chunk_size": None,    # fits in one chunk
        "chunk_overlap": 0,
    },
    "amc": {
        "strategy": "recursive_text",
        "max_chunk_size": 800,
        "chunk_overlap": 100,
    },
    "nfo": {
        "strategy": "per_nfo_item",   # One chunk per NFO entry
        "max_chunk_size": 500,
    },
    "market_news": {
        "strategy": "per_article",     # One chunk per news article
        "max_chunk_size": 600,
    },
}
```

---

## 8. Vector Database Synchronization Engine

### 8.1 Sync Decision Matrix

This is the **mandatory** synchronization logic executed every 15 minutes and on admin-triggered sync:

```
┌──────────────────┬──────────────────────────────────────────────────────┐
│ Source State      │ Action                                             │
├──────────────────┼──────────────────────────────────────────────────────┤
│ UNCHANGED        │ No action. Keep existing vectors.                   │
│                  │ Update: last_attempt_at = now, status = 'unchanged' │
├──────────────────┼──────────────────────────────────────────────────────┤
│ CHANGED          │ 1. Delete old vectors for this source_url           │
│                  │ 2. Chunk new content                                │
│                  │ 3. Embed chunks                                     │
│                  │ 4. Insert new vectors with updated metadata         │
│                  │ 5. Archive previous snapshot to previous.json       │
│                  │ 6. Save new snapshot to current.json                │
│                  │ 7. Compute and save diff.json                       │
│                  │ 8. Update: last_attempt_at, last_success_at, hash   │
├──────────────────┼──────────────────────────────────────────────────────┤
│ NEW SOURCE       │ 1. Scrape URL                                       │
│                  │ 2. Parse, extract, validate                         │
│                  │ 3. Chunk content                                    │
│                  │ 4. Embed chunks                                     │
│                  │ 5. Insert vectors                                   │
│                  │ 6. Create initial snapshot                          │
│                  │ 7. Create refresh_status record                     │
├──────────────────┼──────────────────────────────────────────────────────┤
│ DELETED SOURCE   │ 1. Delete ALL vectors where source_url matches      │
│                  │ 2. Mark source_urls.is_active = false               │
│                  │ 3. Remove snapshot files                            │
├──────────────────┼──────────────────────────────────────────────────────┤
│ FAILED SCRAPE    │ 1. DO NOT delete existing vectors                   │
│                  │ 2. Keep previous successful data active             │
│                  │ 3. Record error in scrape_history                   │
│                  │ 4. Update: status = 'failed', error_message, count  │
│                  │ 5. last_success_at remains unchanged                │
└──────────────────┴──────────────────────────────────────────────────────┘
```

### 8.2 Sync Engine Pseudocode

```python
async def run_sync_cycle(trigger_type: str = "scheduler"):
    """
    Main synchronization loop.
    Called every 15 minutes by scheduler OR manually by admin.
    """
    configured_urls = await db.get_active_source_urls()
    existing_url_set = {r.url for r in configured_urls}

    # 1. Detect DELETED sources (previously active, now removed)
    previously_active = await db.get_urls_with_vectors()
    deleted_urls = previously_active - existing_url_set
    for url in deleted_urls:
        await chromadb.delete(where={"source_url": url})
        await db.mark_source_inactive(url)
        delete_snapshots(url)

    # 2. Process each configured URL
    for source in configured_urls:
        try:
            # Scrape
            raw_content = await scraper.scrape(source.url, source.source_type)
            extracted = parser.extract(raw_content, source.source_type)
            new_hash = compute_content_hash(extracted)

            # Check if changed
            old_hash = await db.get_content_hash(source.id)

            if old_hash == new_hash:
                # UNCHANGED
                await db.update_refresh_status(
                    source.id, status="unchanged",
                    last_attempt_at=now()
                )
                continue

            if old_hash is None:
                # NEW SOURCE
                pass  # fall through to embed + insert

            # CHANGED or NEW — re-embed
            # Delete old vectors for this source
            await chromadb.delete(where={"source_url": source.url})

            # Chunk and embed
            chunks = chunker.chunk(extracted, source.source_type)
            embeddings = embedding_model.encode([c.text for c in chunks])

            # Insert new vectors
            await chromadb.add(
                ids=[c.id for c in chunks],
                documents=[c.text for c in chunks],
                embeddings=embeddings,
                metadatas=[c.metadata for c in chunks]
            )

            # Update snapshots
            rotate_snapshots(source.url, extracted)
            compute_and_save_diff(source.url)

            # Update DB
            await db.update_refresh_status(
                source.id, status="success",
                last_attempt_at=now(), last_success_at=now(),
                content_hash=new_hash
            )

            # Track NFO / News changes
            if source.source_type == "nfo":
                await nfo_tracker.process_changes(extracted)
            elif source.source_type == "market_news":
                await news_tracker.process_changes(extracted)

            await db.log_scrape_history(source.id, "success", new_hash, trigger_type)

        except Exception as e:
            # FAILED — retain previous vectors
            await db.update_refresh_status(
                source.id, status="failed",
                last_attempt_at=now(),
                error_message=str(e),
                error_count=increment
            )
            await db.log_scrape_history(source.id, "failed", None, trigger_type, str(e))
```

---

## 9. RAG Query Pipeline

### 9.1 Query Classification

The query classifier determines the intent and routes to the appropriate retrieval strategy:

```python
QUERY_TYPES = {
    "fund_lookup":      "Single fund information query",
    "fund_comparison":  "Compare two or more funds",
    "nfo_query":        "NFO discovery or status question",
    "news_query":       "Market news search or summary",
    "category_search":  "Find funds by category/theme/AMC",
    "metric_search":    "Find funds by a specific metric (lowest expense ratio, etc.)",
    "freshness_query":  "Data freshness or last-update question",
    "change_query":     "What changed since last refresh",
    "advice_request":   "Investment advice request (BLOCK)",
    "general":          "General or ambiguous query",
}
```

### 9.2 Retrieval Strategy

```python
class GroundedRetriever:
    """Multi-strategy retriever with source-type filtering."""

    async def retrieve(self, query: str, query_type: str, filters: dict) -> list:
        # Build ChromaDB where clause
        where_clause = {}
        if filters.get("source_type"):
            where_clause["source_type"] = filters["source_type"]
        if filters.get("fund_name"):
            where_clause["fund_name"] = {"$contains": filters["fund_name"]}

        # Similarity search with metadata filtering
        results = await chromadb.query(
            query_texts=[query],
            n_results=10,
            where=where_clause if where_clause else None,
        )

        # For comparisons, ensure we have docs for ALL requested funds
        if query_type == "fund_comparison":
            results = self._ensure_multi_fund_coverage(results, filters["fund_names"])

        return results
```

### 9.3 Grounded Prompt Template

```python
SYSTEM_PROMPT = """You are a Groww Market Intelligence assistant. You operate in
STRICT SOURCE-ONLY MODE.

ABSOLUTE RULES:
1. Answer ONLY using the provided source context below. Do NOT use your own knowledge.
2. If the context does not contain the answer, respond EXACTLY with:
   "Currently I dont have the data to answer the query"
3. NEVER provide investment advice, buy/sell/hold recommendations, portfolio
   suggestions, return predictions, or timing recommendations.
4. If asked for advice, politely decline and offer factual information instead.
5. For comparisons, present factual data side-by-side. Do NOT declare winners
   or make recommendations.
6. Always cite the source type and last refresh time when presenting data.
7. Show "N/A" or "Not available in source data" for missing fields.
8. Do NOT infer, calculate, or extrapolate values not explicitly in the context.

SOURCE CONTEXT:
{context}

SOURCE METADATA:
{source_metadata}

CONVERSATION HISTORY:
{chat_history}
"""
```

### 9.4 Grounding Guardrail (Post-Generation Filter)

```python
class GroundingGuardrail:
    """
    Post-generation filter that validates the LLM response
    is grounded in the retrieved context.
    """

    ADVICE_PATTERNS = [
        r"you should (buy|sell|invest|avoid)",
        r"(buy|sell|hold) this",
        r"I (recommend|suggest|advise)",
        r"guaranteed to",
        r"will (go up|increase|decrease|crash)",
        r"best (time|opportunity) to",
        r"(buy now|sell now|wait)",
    ]

    def validate(self, response: str, context: str) -> tuple:
        # 1. Check for advice patterns
        for pattern in self.ADVICE_PATTERNS:
            if re.search(pattern, response, re.IGNORECASE):
                return False, self._generate_advice_decline()

        # 2. Check key claims are grounded in context
        # (Extract numeric values from response, verify they appear in context)

        return True, response
```

---

## 10. Conversation Management

### 10.1 Memory Architecture

```python
class ConversationManager:
    """
    Manages per-session conversation history for follow-up resolution.
    Uses LangChain ConversationBufferWindowMemory.
    """

    def __init__(self):
        self.sessions = {}  # session_id -> ConversationMemory

    def get_or_create(self, session_id: str):
        if session_id not in self.sessions:
            self.sessions[session_id] = ConversationBufferWindowMemory(
                k=10,               # Last 10 exchanges
                memory_key="chat_history",
                return_messages=True,
            )
        return self.sessions[session_id]
```

### 10.2 Follow-Up Resolution

When the user says "this fund" or "the second one":

1. Extract entity references from the latest message.
2. Search the conversation history for the most recent fund/entity context.
3. Resolve the reference to a concrete entity.
4. If ambiguous, ask clarification rather than guessing.

---

## 11. Admin Subsystem

### 11.1 Authentication Flow

```mermaid
sequenceDiagram
    participant Admin
    participant Frontend
    participant API
    participant DB

    Admin->>Frontend: Navigate to /admin/login
    Admin->>Frontend: Enter admin / admin
    Frontend->>API: POST /api/admin/login {username, password}
    API->>DB: Lookup admin_users, verify bcrypt hash
    DB-->>API: User found, hash matches
    API-->>Frontend: { access_token: "eyJ..." }
    Frontend->>Frontend: Store JWT in memory (not localStorage)
    Frontend->>API: GET /api/admin/urls (Authorization: Bearer eyJ...)
    API->>API: Verify JWT middleware
    API->>DB: SELECT * FROM source_urls WHERE is_active = true
    DB-->>API: URL list
    API-->>Frontend: URL list JSON
```

### 11.2 URL Management & Sync Trigger

```mermaid
sequenceDiagram
    participant Admin
    participant API
    participant Scheduler
    participant Scraper
    participant ChromaDB

    Admin->>API: POST /api/admin/urls {url, source_type}
    API->>API: Validate URL format (must be groww.in domain)
    API-->>Admin: 201 Created

    Admin->>API: DELETE /api/admin/urls/5
    API-->>Admin: 200 OK

    Admin->>API: POST /api/admin/sync
    API->>Scheduler: Trigger immediate sync cycle (trigger_type: admin_manual)
    Scheduler->>Scraper: Run full sync cycle
    Scraper->>ChromaDB: Apply sync decision matrix
    Scheduler-->>API: Sync complete
    API-->>Admin: { status: completed, results: {...} }
```

### 11.3 Admin Dashboard Data

```json
// GET /api/admin/status response
{
    "overall": {
        "total_sources": 33,
        "healthy_sources": 31,
        "failed_sources": 2,
        "last_global_refresh": "2026-08-25T13:30:00+05:30",
        "next_scheduled_refresh": "2026-08-25T13:45:00+05:30",
        "refresh_in_progress": false
    },
    "sources": [
        {
            "id": 1,
            "url": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
            "source_type": "mutual_fund",
            "label": "HDFC Mid Cap Fund",
            "status": "success",
            "last_attempt_at": "2026-08-25T13:30:05+05:30",
            "last_success_at": "2026-08-25T13:30:05+05:30",
            "content_hash": "a1b2c3...",
            "error_message": null,
            "error_count": 0
        },
        {
            "id": 15,
            "url": "https://groww.in/mutual-funds/nippon-india-small-cap-fund-direct-growth",
            "source_type": "mutual_fund",
            "label": "Nippon India Small Cap Fund",
            "status": "failed",
            "last_attempt_at": "2026-08-25T13:30:12+05:30",
            "last_success_at": "2026-08-25T13:15:08+05:30",
            "content_hash": "d4e5f6...",
            "error_message": "Timeout: page load exceeded 30s",
            "error_count": 1
        }
    ]
}
```

---

## 12. Notification Subsystem

### 12.1 NFO Change Detection

```python
async def detect_nfo_changes(current_nfos: list, previous_nfos: list):
    """
    Compare current and previous NFO snapshots.
    Returns: new NFOs, changed NFOs, removed NFOs.
    """
    current_set = {nfo["nfo_name"]: nfo for nfo in current_nfos}
    previous_set = {nfo["nfo_name"]: nfo for nfo in previous_nfos}

    new_nfos = [v for k, v in current_set.items() if k not in previous_set]
    removed_nfos = [v for k, v in previous_set.items() if k not in current_set]
    changed_nfos = [
        {"nfo": current_set[k], "changes": diff(previous_set[k], current_set[k])}
        for k in current_set
        if k in previous_set and current_set[k] != previous_set[k]
    ]

    return new_nfos, changed_nfos, removed_nfos
```

### 12.2 Notification Delivery

Notifications are **pull-based** (polled by the frontend) rather than push-based, to avoid requiring a persistent connection:

```
GET /api/data/notifications?session_id=xyz

Response:
{
    "notifications": [
        {
            "id": "notif_001",
            "type": "new_nfo",
            "title": "New NFO: HDFC Innovation Fund",
            "body": "A new NFO from HDFC Mutual Fund was detected...",
            "created_at": "2026-08-25T13:30:00+05:30",
            "read": false
        }
    ]
}
```

---

## 13. Frontend Architecture

### 13.1 Route Structure

```
/                       → Chat page (default, no login)
/compare                → Fund comparison workspace
/nfo                    → NFO discovery page
/news                   → Market news feed
/watchlist              → User's saved topics
/admin/login            → Admin login form
/admin/dashboard        → Admin URL management + status (JWT required)
```

### 13.2 Component Hierarchy

```
<App>
├── <SourceOnlyBanner />              ← "Groww Source-Only Mode" persistent indicator
├── <FreshnessStatusBar />            ← Global data availability indicator (green/amber/red)
├── <Navigation />
│   ├── Chat | Compare | NFO | News | Watchlist
│   └── Admin (only visible after login)
│
├── <ChatPage>
│   ├── <ChatMessageList>
│   │   ├── <UserMessage />
│   │   └── <AssistantMessage>
│   │       ├── <MarkdownRenderer />
│   │       ├── <ComparisonTable />    ← Inline comparison if query was comparison-type
│   │       └── <SourceCitation />     ← Source URL + type + timestamp
│   └── <ChatInput />
│
├── <ComparePage>
│   ├── <FundSelector />               ← Multi-select from available funds
│   └── <ComparisonGrid />             ← Side-by-side metrics, "N/A" for missing
│
├── <NFOPage>
│   ├── <NFOFilterBar />
│   ├── <NFOList>
│   │   └── <NFOCard />                ← Status badge, "NEW" tag, dates
│   └── <NFONotificationToggle />
│
├── <NewsPage>
│   ├── <NewsSearchBar />
│   ├── <NewsList>
│   │   └── <NewsCard />               ← Title, time, summary, "NEW" tag
│   └── <NewsNotificationToggle />
│
├── <WatchlistPage>
│   ├── <WatchlistItems />
│   └── <ChangesSummary />             ← Detected changes for watched items
│
└── <AdminDashboard>                   ← Protected by JWT check
    ├── <URLManager>
    │   ├── <URLTable />               ← List, add, delete URLs
    │   └── <SyncButton />             ← Trigger manual refresh
    └── <RefreshStatusPanel>
        ├── <OverallStatus />
        └── <PerSourceStatusTable />   ← Status, timestamps, error details
```

### 13.3 Data Availability Indicator States

```css
/* Freshness indicator color coding */
.freshness-status--healthy    { color: #22c55e; } /* Green  — refreshed < 15 min ago */
.freshness-status--stale      { color: #f59e0b; } /* Amber  — refreshed > 15 min ago */
.freshness-status--failed     { color: #ef4444; } /* Red    — source scrape failed */
.freshness-status--unavailable{ color: #6b7280; } /* Grey   — no data collected yet */
```

---

## 14. Security Architecture

### 14.1 Access Control Matrix

```
┌─────────────────────────┬──────────────┬──────────────┐
│ Capability              │ Normal User  │ Admin        │
├─────────────────────────┼──────────────┼──────────────┤
│ Chat with bot           │ ✅           │ ✅           │
│ View fund data          │ ✅           │ ✅           │
│ Compare funds           │ ✅           │ ✅           │
│ View NFOs               │ ✅           │ ✅           │
│ View market news        │ ✅           │ ✅           │
│ Manage watchlist        │ ✅           │ ✅           │
│ Set notifications       │ ✅           │ ✅           │
│ Login to admin          │ ❌           │ ✅           │
│ View scraping URLs      │ ❌           │ ✅           │
│ Add/remove URLs         │ ❌           │ ✅           │
│ Trigger manual sync     │ ❌           │ ✅           │
│ View refresh status     │ ❌           │ ✅           │
│ View scraping errors    │ ❌           │ ✅           │
└─────────────────────────┴──────────────┴──────────────┘
```

### 14.2 Security Measures

| Concern | Measure |
|---|---|
| Admin auth | bcrypt-hashed passwords, JWT with 1-hour expiry, HTTP-only secure flag |
| Admin routes | FastAPI `Depends(verify_jwt)` middleware on all `/api/admin/*` routes |
| User sessions | Random UUID session ID stored in `localStorage`, no PII collected |
| Input validation | Pydantic models for all request bodies, URL validation for groww.in domain |
| Rate limiting | `slowapi` rate limiter: 30 req/min for chat, 10 req/min for admin |
| CORS | Whitelist frontend origin only |
| Scraper safety | Headless browser sandboxed, no file uploads, no script execution from scraped content |
| LLM safety | System prompt hardcoded (not user-modifiable), guardrail post-filter on every response |

---

## 15. Deployment Architecture

### 15.1 Single-Server Development Deployment

```
┌─────────────────────────────────────────────────────────┐
│                   Docker Compose Stack                   │
├───────────────┬──────────────┬──────────────────────────┤
│ frontend      │ backend      │ postgres                 │
│ (Node/Vite)   │ (FastAPI +   │ (PostgreSQL 15)          │
│ Port 3000     │  Uvicorn)    │ Port 5432                │
│               │ Port 8000    │                          │
│               │              │                          │
│               │ ChromaDB     │                          │
│               │ (embedded)   │                          │
│               │              │                          │
│               │ Playwright   │                          │
│               │ (headless    │                          │
│               │  Chromium)   │                          │
└───────────────┴──────────────┴──────────────────────────┘
```

### 15.2 Environment Variables

```env
# Backend
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/rag_grow
CHROMA_PERSIST_DIR=./data/chromadb
SNAPSHOT_DIR=./data/snapshots
GROK_API_KEY=<your-grok-api-key>
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
JWT_SECRET_KEY=<random-secret>
JWT_EXPIRY_HOURS=1
SCRAPE_INTERVAL_MINUTES=15
SCRAPE_TIMEOUT_SECONDS=30
SCRAPE_MAX_CONCURRENT=5
ADMIN_DEFAULT_USERNAME=admin
ADMIN_DEFAULT_PASSWORD=admin
CORS_ORIGINS=http://localhost:3000

# Frontend
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

---

## 16. Error Handling & Resilience

### 16.1 Scraping Resilience

```python
class ResilientScraper:
    MAX_RETRIES = 2
    RETRY_DELAY_SECONDS = 5
    PAGE_TIMEOUT_MS = 30_000

    async def scrape_with_retry(self, url: str):
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                page = await self.browser.new_page()
                await page.goto(url, timeout=self.PAGE_TIMEOUT_MS, wait_until="networkidle")
                content = await page.content()
                await page.close()
                return ScrapedContent(url=url, html=content, status="success")
            except TimeoutError:
                if attempt < self.MAX_RETRIES:
                    await asyncio.sleep(self.RETRY_DELAY_SECONDS)
                    continue
                raise ScrapeFailedError(url, "Timeout after retries")
            except Exception as e:
                if attempt < self.MAX_RETRIES:
                    await asyncio.sleep(self.RETRY_DELAY_SECONDS)
                    continue
                raise ScrapeFailedError(url, str(e))
```

### 16.2 Failure Handling Matrix

| Failure Type | Impact | Handling |
|---|---|---|
| Single source scrape timeout | That source only | Retain previous vectors, log failure, continue cycle |
| All sources fail (network down) | All sources | Retain all vectors, mark all as failed, alert admin |
| ChromaDB write error | Sync for that source | Retry once, then log error and retain previous state |
| PostgreSQL unavailable | Metadata writes | Queue status updates in memory, flush on reconnect |
| LLM API error | Single user query | Return "Service temporarily unavailable, please retry" |
| Embedding model OOM | Sync cycle | Process sources serially with smaller batch sizes |

---

## 17. Directory Structure

```
RAG_for_GROW/
├── docs/
│   └── problemStatement.txt
├── problemStatement.md
├── architecture.md
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                      # FastAPI app factory, startup events
│   │   ├── config.py                    # Settings from env vars (Pydantic Settings)
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py                  # WebSocket chat endpoint
│   │   │   ├── data.py                  # Public data REST endpoints
│   │   │   ├── admin.py                 # Admin REST endpoints (JWT-protected)
│   │   │   └── deps.py                  # Dependency injection (DB sessions, auth)
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── db_models.py             # SQLAlchemy ORM models
│   │   │   └── schemas.py               # Pydantic request/response schemas
│   │   │
│   │   ├── scraper/
│   │   │   ├── __init__.py
│   │   │   ├── engine.py                # Playwright scraper engine
│   │   │   ├── extractors/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── mutual_fund.py       # Mutual fund page extractor
│   │   │   │   ├── amc.py               # AMC page extractor
│   │   │   │   ├── nfo.py               # NFO page extractor
│   │   │   │   ├── market_news.py       # Share market today extractor
│   │   │   │   └── filter_page.py       # Filter/listing page extractor
│   │   │   ├── normalizer.py            # Data cleaning & normalization
│   │   │   └── validator.py             # Extracted data validation
│   │   │
│   │   ├── pipeline/
│   │   │   ├── __init__.py
│   │   │   ├── scheduler.py             # APScheduler setup (15-min interval)
│   │   │   ├── sync_engine.py           # Vector DB sync decision engine
│   │   │   ├── chunker.py               # Content chunking strategies
│   │   │   ├── embedder.py              # Embedding generation
│   │   │   ├── change_detector.py       # Content hashing & diff computation
│   │   │   ├── snapshot_manager.py      # Current/previous JSON snapshot management
│   │   │   ├── nfo_tracker.py           # NFO change detection & tracking
│   │   │   └── news_tracker.py          # News change detection & tracking
│   │   │
│   │   ├── rag/
│   │   │   ├── __init__.py
│   │   │   ├── query_classifier.py      # Intent classification
│   │   │   ├── retriever.py             # ChromaDB retriever with filtering
│   │   │   ├── prompt_templates.py      # System prompt, grounding instructions
│   │   │   ├── generator.py             # LLM call with grounding context
│   │   │   ├── guardrail.py             # Post-generation grounding & advice filter
│   │   │   └── conversation.py          # Conversation memory management
│   │   │
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── jwt_handler.py           # JWT creation & verification
│   │   │   └── password.py              # bcrypt hashing
│   │   │
│   │   ├── notifications/
│   │   │   ├── __init__.py
│   │   │   └── notification_service.py  # NFO & news notification engine
│   │   │
│   │   └── db/
│   │       ├── __init__.py
│   │       ├── session.py               # Async SQLAlchemy session factory
│   │       ├── init_db.py               # Table creation, seed admin user
│   │       └── migrations/              # Alembic migration scripts
│   │
│   ├── data/
│   │   ├── chromadb/                    # ChromaDB persistent storage
│   │   └── snapshots/                   # JSON snapshots per source
│   │
│   ├── tests/
│   │   ├── test_scraper.py
│   │   ├── test_sync_engine.py
│   │   ├── test_rag_pipeline.py
│   │   ├── test_guardrail.py
│   │   ├── test_admin_api.py
│   │   └── test_chat_api.py
│   │
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── index.css                    # Design system tokens & global styles
│   │   │
│   │   ├── components/
│   │   │   ├── chat/
│   │   │   │   ├── ChatWindow.jsx
│   │   │   │   ├── ChatInput.jsx
│   │   │   │   ├── ChatMessage.jsx
│   │   │   │   ├── SourceCitation.jsx
│   │   │   │   └── ComparisonTable.jsx
│   │   │   ├── common/
│   │   │   │   ├── SourceOnlyBanner.jsx
│   │   │   │   ├── FreshnessIndicator.jsx
│   │   │   │   ├── Navigation.jsx
│   │   │   │   └── LoadingSpinner.jsx
│   │   │   ├── nfo/
│   │   │   │   ├── NFOCard.jsx
│   │   │   │   └── NFOList.jsx
│   │   │   ├── news/
│   │   │   │   ├── NewsCard.jsx
│   │   │   │   └── NewsList.jsx
│   │   │   ├── compare/
│   │   │   │   ├── FundSelector.jsx
│   │   │   │   └── ComparisonGrid.jsx
│   │   │   ├── watchlist/
│   │   │   │   ├── WatchlistPanel.jsx
│   │   │   │   └── ChangesSummary.jsx
│   │   │   └── admin/
│   │   │       ├── AdminLogin.jsx
│   │   │       ├── URLManager.jsx
│   │   │       ├── SyncButton.jsx
│   │   │       └── RefreshStatusPanel.jsx
│   │   │
│   │   ├── pages/
│   │   │   ├── ChatPage.jsx
│   │   │   ├── ComparePage.jsx
│   │   │   ├── NFOPage.jsx
│   │   │   ├── NewsPage.jsx
│   │   │   ├── WatchlistPage.jsx
│   │   │   ├── AdminLoginPage.jsx
│   │   │   └── AdminDashboardPage.jsx
│   │   │
│   │   ├── context/
│   │   │   ├── AuthContext.jsx
│   │   │   ├── ChatContext.jsx
│   │   │   └── FreshnessContext.jsx
│   │   │
│   │   ├── hooks/
│   │   │   ├── useWebSocket.js
│   │   │   ├── useFreshness.js
│   │   │   └── useNotifications.js
│   │   │
│   │   ├── services/
│   │   │   ├── api.js                   # Axios instance with JWT interceptor
│   │   │   ├── chatService.js
│   │   │   ├── dataService.js
│   │   │   └── adminService.js
│   │   │
│   │   └── utils/
│   │       ├── formatters.js
│   │       └── constants.js
│   │
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
│
├── docker-compose.yml
├── .gitignore
└── README.md
```

# Groww Market Intelligence — Edge Cases & Failure Scenarios

> **Derived from:**
> - [architecture.md](file:///d:/GenAI/Practice/Pranju/RAG_for_GROW/docs/architecture.md)
> - [implementation-plan.md](file:///d:/GenAI/Practice/Pranju/RAG_for_GROW/docs/implementation-plan.md)

---

## Table of Contents

1. [Scraping & Content Extraction](#1-scraping--content-extraction)
2. [Content Hashing & Change Detection](#2-content-hashing--change-detection)
3. [Vector DB Sync Engine (5-State Matrix)](#3-vector-db-sync-engine-5-state-matrix)
4. [Embedding & Chunking Pipeline](#4-embedding--chunking-pipeline)
5. [RAG Query Pipeline](#5-rag-query-pipeline)
6. [Grounding & Guardrails](#6-grounding--guardrails)
7. [Conversation Management](#7-conversation-management)
8. [Admin Subsystem](#8-admin-subsystem)
9. [Authentication & Security](#9-authentication--security)
10. [Frontend & WebSocket](#10-frontend--websocket)
11. [Notification Subsystem](#11-notification-subsystem)
12. [Data Freshness & Availability](#12-data-freshness--availability)
13. [Infrastructure & Persistence](#13-infrastructure--persistence)
14. [Deployment & Environment](#14-deployment--environment)
15. [Concurrency & Race Conditions](#15-concurrency--race-conditions)

---

## 1. Scraping & Content Extraction

### 1.1 Network & Timeout Failures

| # | Edge Case | Expected Behaviour | Source Reference |
|---|-----------|-------------------|-----------------|
| 1.1.1 | **Single source page load exceeds 30 s timeout** | `ResilientScraper` retries up to 2 times with 5 s delay. After final failure, raises `ScrapeFailedError`; vectors for this source are **retained** (not deleted). Error logged to `scrape_history` with `status = 'failed'`. | Architecture §16.1, §8.1 |
| 1.1.2 | **All 33 sources fail (complete network outage)** | Every source enters the FAILED path. **All existing vectors are retained.** All sources marked `status = 'failed'` in `refresh_status`. Admin alerted via status dashboard. Chat continues using last-good data. | Architecture §16.2 |
| 1.1.3 | **Intermittent network: first retry fails, second succeeds** | `ResilientScraper` completes on 2nd attempt. `scrape_history` records `status = 'success'`. No data loss. | Architecture §16.1 |
| 1.1.4 | **DNS resolution failure for groww.in** | Treated as a scrape timeout/error. Same retry + FAILED path handling. | Architecture §16.1 |
| 1.1.5 | **Groww returns HTTP 429 (rate-limited) or 403 (blocked)** | Playwright receives error page. Extractor fails validation (mandatory fields missing). Enters FAILED path — old vectors preserved. | Implementation §2.5, Architecture §16.2 |

### 1.2 Page Structure & Content Changes

| # | Edge Case | Expected Behaviour | Source Reference |
|---|-----------|-------------------|-----------------|
| 1.2.1 | **Groww redesigns fund page HTML structure** | CSS selectors in `MutualFundScraper` fail to locate elements. `validator.py` rejects the extraction (missing mandatory fields like `fund_name`). FAILED path triggered — old vectors retained. Error logged for admin review. | Implementation §2.3, §2.5 |
| 1.2.2 | **A fund page is temporarily down / returns blank body** | Completely empty extraction rejected by `validator.py`. FAILED path — old data preserved. | Implementation §2.3 |
| 1.2.3 | **Page loads but optional fields are missing** (e.g., no 10-year returns for a new fund) | `normalizer.py` handles `"N/A"`, `"-"`, and empty fields gracefully. The field is stored as null/empty in the snapshot. UI renders `"N/A"`. | Implementation §2.3, Architecture §9.3 Rule 7 |
| 1.2.4 | **Currency/number format change** (e.g., `₹56,789` → `56789.00`) | `normalizer.py` strips whitespace, normalizes `₹` symbol, parses percentage strings. If format is unrecognised, the raw value is preserved. | Implementation §2.3 |
| 1.2.5 | **Date format change on Groww** (e.g., `22 Aug 2026` → `2026-08-22`) | `normalizer.py` parses dates to ISO 8601. If parsing fails, stores raw string and logs warning. | Implementation §2.3 |
| 1.2.6 | **NFO page has zero NFOs listed** (no open NFOs currently) | Extractor returns empty list. Valid extraction (not rejected). ChromaDB will have no NFO-type documents. Chat responds with exact fallback: *"Currently I dont have the data to answer the query"*. | Architecture §9.3 Rule 2 |
| 1.2.7 | **News page returns duplicate articles across scrapes** | Content hash comparison (`SHA-256`) detects UNCHANGED. Sync engine skips re-embedding. `news_tracking` table deduplicates by `content_hash`. | Architecture §8.1, Implementation §3.5 |

### 1.3 Browser & Playwright Issues

| # | Edge Case | Expected Behaviour | Source Reference |
|---|-----------|-------------------|-----------------|
| 1.3.1 | **Playwright Chromium process crashes** | Scrape fails, enters FAILED path. On next cycle, `ScraperEngine.initialize()` re-launches the browser. | Architecture §16.2 |
| 1.3.2 | **Playwright memory leak from long-running browser** | Browser context pool has max lifetime. Periodic browser restart mitigates OOM. | Implementation §Risk Mitigation |
| 1.3.3 | **Browser context pool exhausted (5 concurrent max)** | Additional scrape tasks queue until a context is freed. Worst case: scrape cycle takes longer but does not crash. | Architecture §7.1 |
| 1.3.4 | **JavaScript-rendered content not fully loaded** | Playwright waits until `networkidle`. If content is still incomplete, partial extraction occurs. Validator checks for mandatory fields. | Architecture §16.1 |

---

## 2. Content Hashing & Change Detection

| # | Edge Case | Expected Behaviour | Source Reference |
|---|-----------|-------------------|-----------------|
| 2.1 | **Page content identical across two cycles** | `compute_content_hash()` returns same SHA-256. Sync engine marks source as UNCHANGED — no re-embedding. | Architecture §8.1 |
| 2.2 | **Only whitespace/formatting changes on page** (no actual data change) | `normalizer.py` strips whitespace before hashing, so trivial changes produce the same hash → treated as UNCHANGED. | Implementation §2.3, §2.4 |
| 2.3 | **Single field changes** (e.g., NAV updates daily) | Hash differs → CHANGED path. Full re-chunk + re-embed for this source. Diff snapshot records the specific field change. | Architecture §8.1 |
| 2.4 | **Hash collision** (two different contents produce same SHA-256) | Astronomically unlikely (SHA-256 collision). If it occurs, content treated as UNCHANGED and stale data remains. Acceptable risk. | Architecture §7.3 |
| 2.5 | **First-ever scrape of a source (no previous hash)** | `old_hash is None` → treated as NEW source. Scrape, chunk, embed, insert. Create initial `current.json` snapshot. | Architecture §8.1, §8.2 |

---

## 3. Vector DB Sync Engine (5-State Matrix)

This is the **mandatory core logic**. Each state must be handled exactly as specified.

| # | State | Edge Case | Expected Behaviour | Source Reference |
|---|-------|-----------|-------------------|-----------------|
| 3.1 | **UNCHANGED** | Source scraped successfully, hash matches previous | No vector action. Update `last_attempt_at = now`, `status = 'unchanged'`. No snapshot change. | Architecture §8.1 |
| 3.2 | **CHANGED** | Source scraped, hash differs from previous | Delete old vectors for this `source_url` → chunk new content → embed → insert new vectors. Rotate `current.json → previous.json`, save new `current.json`, compute `diff.json`. Update `last_attempt_at`, `last_success_at`, `content_hash`. | Architecture §8.1 |
| 3.3 | **NEW** | Admin adds a URL that has never been scraped | Scrape → parse → validate → chunk → embed → insert vectors. Create `refresh_status` row with `status = 'success'`. Create initial `current.json` snapshot. No previous.json or diff.json yet. | Architecture §8.1 |
| 3.4 | **DELETED** | Admin removes a URL | Delete **ALL** vectors where `source_url` matches in ChromaDB. Set `source_urls.is_active = false`, `removed_at = now`. Delete snapshot directory for this URL. | Architecture §8.1 |
| 3.5 | **FAILED** | Scrape attempt throws an exception | **DO NOT delete** existing vectors. Retain previous successful data. Record error in `scrape_history`. Update `status = 'failed'`, increment `error_count`, set `error_message`. **DO NOT update** `last_success_at`. | Architecture §8.1 |
| 3.6 | **FAILED after previously FAILED** | Source fails for N consecutive cycles | `error_count` increments each time. `last_success_at` remains at the time of last successful scrape. Old vectors continue serving queries with stale (but real) data. | Architecture §8.1, §8.2 |
| 3.7 | **DELETED source that also FAILED previously** | Admin deletes a source that was already in failed state | Vectors from the last successful scrape are deleted. Source marked inactive. Snapshots removed. | Architecture §8.1 |
| 3.8 | **NEW source where scrape immediately fails** | Freshly added URL is unreachable | No vectors inserted. `refresh_status` row created with `status = 'failed'`. No snapshot files created. Queries about this source return fallback response. | Architecture §8.1 |
| 3.9 | **Admin triggers manual sync while scheduler sync is running** | Potential race condition (see §15). Should either queue or reject the manual sync with a "refresh in progress" message. `system_state.refresh_in_progress` flag prevents concurrent runs. | Architecture §11.2, Implementation §5.3 |

---

## 4. Embedding & Chunking Pipeline

| # | Edge Case | Expected Behaviour | Source Reference |
|---|-----------|-------------------|-----------------|
| 4.1 | **Embedding model fails to load** (file corrupt, disk full) | Application startup fails. Backend cannot process any queries or sync. Must be treated as a critical error — logged and surfaced. | Implementation §3.2 |
| 4.2 | **Embedding model OOM on large batch** | Process sources serially with smaller batch sizes instead of parallel embedding. | Architecture §16.2 |
| 4.3 | **Chunk size exceeds max token limit** | Section-based chunking for mutual funds splits by predefined sections (overview, returns, holdings, etc.). `max_chunk_size` with overlap ensures no single chunk exceeds limits. | Architecture §7.4 |
| 4.4 | **Source content is extremely short** (e.g., an NFO entry of 50 tokens) | Per-NFO chunking produces one very small chunk. This is valid — no minimum chunk size enforced. | Architecture §7.4 |
| 4.5 | **Source content is extremely long** (e.g., AMC page with hundreds of funds) | Recursive text splitter with `max_chunk_size = 800` and `overlap = 100` handles pagination. May produce many chunks. | Architecture §7.4 |
| 4.6 | **ChromaDB collection does not exist on first startup** | `embedder.py` creates the `groww_funds` collection with cosine similarity on initialisation. | Implementation §3.1 |

---

## 5. RAG Query Pipeline

### 5.1 Query Classification

| # | Edge Case | Expected Behaviour | Source Reference |
|---|-----------|-------------------|-----------------|
| 5.1.1 | **Ambiguous query** (e.g., "Tell me about funds") | Classified as `general`. Broad retrieval across all `mutual_fund` sources, limited results. | Architecture §9.1 |
| 5.1.2 | **Query mixes intent types** (e.g., "Compare HDFC Mid Cap with latest NFOs") | Classifier picks dominant intent. May need to issue multiple retrieval queries. | Architecture §9.1 |
| 5.1.3 | **Non-financial query** (e.g., "What is the weather?") | No relevant vectors found. Response: *"Currently I dont have the data to answer the query"*. | Architecture §9.3 Rule 2 |
| 5.1.4 | **Misspelled fund name** (e.g., "HFDC Mid Cap") | Similarity search in ChromaDB may still match "HDFC Mid Cap" if embedding captures semantic closeness. If no match, returns fallback. | Architecture §9.2 |
| 5.1.5 | **Query about a fund not in the 33 sources** | No vectors exist for that fund. Returns exact fallback message. | Architecture §9.3 Rule 2 |

### 5.2 Retrieval

| # | Edge Case | Expected Behaviour | Source Reference |
|---|-----------|-------------------|-----------------|
| 5.2.1 | **Empty ChromaDB (first startup before initial sync)** | Zero results returned. Chat shows *"Currently I dont have the data to answer the query"*. UI shows "Initial data loading…" indicator. | Implementation §7.8 |
| 5.2.2 | **Fund comparison where one fund has no data** | `_ensure_multi_fund_coverage()` detects missing fund. Response shows available data for present funds and `"N/A"` for the missing fund's fields. | Architecture §9.2, §9.3 Rule 7 |
| 5.2.3 | **Comparison request with > 5 funds** | Retriever runs multiple queries (5 per fund). May produce very large context. LLM may truncate — should still present available data side-by-side. | Architecture §9.2 |
| 5.2.4 | **Freshness query** (e.g., "When was this data last updated?") | Does NOT query ChromaDB. Queries `refresh_status` table in PostgreSQL directly. Returns per-source timestamps. | Architecture §9.2 |
| 5.2.5 | **Change query** (e.g., "What changed in HDFC Mid Cap?") | Does NOT query ChromaDB. Reads `diff.json` snapshot from disk. If no diff exists (first scrape), responds that no previous data is available for comparison. | Architecture §9.2, Implementation §7.3 |

---

## 6. Grounding & Guardrails

| # | Edge Case | Expected Behaviour | Source Reference |
|---|-----------|-------------------|-----------------|
| 6.1 | **User asks "Should I buy HDFC Mid Cap Fund?"** | Query classified as `advice_request` → **blocked immediately** before retrieval. Returns polite decline offering factual information instead. | Architecture §9.1, §9.3 Rule 3 |
| 6.2 | **LLM generates advice despite system prompt** (e.g., "You should invest in…") | Post-generation `GroundingGuardrail` catches advice patterns via regex (`"you should buy/sell/invest/avoid"`, `"I recommend/suggest/advise"`, `"guaranteed to"`, `"will go up/increase/decrease/crash"`, `"best time/opportunity to"`, `"buy now/sell now/wait"`). Response replaced with advice decline. | Architecture §9.4 |
| 6.3 | **LLM hallucinates a numeric value not in context** (e.g., invents an NAV) | Guardrail extracts numeric claims from response and verifies they appear in the source context. If not grounded, response is replaced with fallback. | Architecture §9.4 |
| 6.4 | **LLM produces comparison with a "winner" declaration** | System prompt Rule 5 prohibits declaring winners. If guardrail detects ranking language, the response is filtered. | Architecture §9.3 Rule 5 |
| 6.5 | **User asks for a prediction** (e.g., "Will this fund go up next month?") | Caught by both query classifier (advice_request) and guardrail patterns (`"will go up/increase/decrease/crash"`). Double-blocked. | Architecture §9.1, §9.4 |
| 6.6 | **User asks an indirect advice question** (e.g., "Is this a good fund?") | May not trigger regex patterns. System prompt Rule 3 instructs the LLM to decline. If the LLM still answers with opinion, guardrail may not catch all indirect phrasing — acceptable residual risk. | Architecture §9.3, §9.4 |
| 6.7 | **Context contains no relevant data for the query** | LLM must respond with the **exact** fallback: *"Currently I dont have the data to answer the query"*. System prompt Rule 2. | Architecture §9.3 Rule 2 |
| 6.8 | **LLM infers/calculates a value not in context** (e.g., computes average returns) | System prompt Rule 8 prohibits inference, calculation, or extrapolation. Guardrail checks for values not in source context. | Architecture §9.3 Rule 8 |

---

## 7. Conversation Management

| # | Edge Case | Expected Behaviour | Source Reference |
|---|-----------|-------------------|-----------------|
| 7.1 | **Follow-up with pronoun reference** (e.g., "What about its returns?") | `ConversationManager` searches last 10 exchanges for the most recent fund/entity. Resolves "its" to that fund. | Architecture §10.2 |
| 7.2 | **Ambiguous follow-up** (e.g., user discussed 3 funds, then says "this fund") | System asks for clarification rather than guessing. | Architecture §10.2 Rule 4 |
| 7.3 | **Session has > 10 exchanges** | `ConversationBufferWindowMemory` with `k=10` drops the oldest exchanges. Older context is lost — follow-ups referencing very old messages may fail to resolve. | Architecture §10.1 |
| 7.4 | **New session with no history** | `get_or_create(session_id)` creates a fresh memory. First query has no conversation context — fully self-contained. | Architecture §10.1 |
| 7.5 | **Server restart clears in-memory sessions** | `ConversationManager` stores sessions in a Python dict (`self.sessions`). Server restart clears all memory. User's follow-up after restart will fail to resolve — acceptable for MVP. | Architecture §10.1 |
| 7.6 | **Multiple concurrent users with different session IDs** | Each session gets independent `ConversationBufferWindowMemory`. No cross-session leakage. | Architecture §10.1 |

---

## 8. Admin Subsystem

| # | Edge Case | Expected Behaviour | Source Reference |
|---|-----------|-------------------|-----------------|
| 8.1 | **Admin adds a non-groww.in URL** | `validate_scraping_url()` rejects it — must be from `groww.in` domain. Returns 400 Bad Request. | Implementation §5.4 |
| 8.2 | **Admin adds a duplicate URL (already active)** | Validation rejects duplicates of existing active URLs. Returns 400 or 409 Conflict. | Implementation §5.4 |
| 8.3 | **Admin adds URL with invalid format** (e.g., missing protocol) | Pydantic validation or URL format check rejects it. Returns 400. | Implementation §5.4 |
| 8.4 | **Admin adds URL that doesn't match expected path patterns** | URL must match one of: `/mutual-funds/*`, `/nfo`, `/share-market-today`, `/mutual-funds/filter*`, `/mutual-funds/amc/*`. Non-matching paths rejected. | Implementation §5.4 |
| 8.5 | **Admin deletes all 33 URLs** | All vectors are deleted from ChromaDB. System continues running but all queries return fallback. `FreshnessIndicator` shows grey (unavailable). | Architecture §8.1 |
| 8.6 | **Admin triggers sync with zero active URLs** | Sync cycle has nothing to process. Returns `{ total: 0 }`. No errors. | Implementation §5.3 |
| 8.7 | **Admin triggers manual sync while automatic sync is in progress** | `system_state.refresh_in_progress` flag should prevent concurrent runs. Manual sync either queues or returns "Refresh already in progress". | Architecture §11.2 |
| 8.8 | **Admin soft-deletes a URL, then re-adds the same URL** | The old row remains with `is_active = false`. New row is created with `is_active = true`. Sync treats it as a NEW source. | Architecture §8.1 |
| 8.9 | **Admin login with wrong credentials** | bcrypt hash comparison fails. Returns 401 Unauthorized. No token issued. | Implementation §5.5 |
| 8.10 | **Admin login with SQL injection attempt in username** | Pydantic model validates input. SQLAlchemy parameterised queries prevent injection. | Architecture §14.2 |

---

## 9. Authentication & Security

| # | Edge Case | Expected Behaviour | Source Reference |
|---|-----------|-------------------|-----------------|
| 9.1 | **JWT token expires (after 1 hour)** | Any admin API call returns 401. Frontend intercepts → redirects to `/admin/login` with "Session expired" message. | Architecture §14.2, Implementation §5.1 |
| 9.2 | **Tampered/invalid JWT token** | `verify_token()` fails signature validation (HS256). Returns 401. | Implementation §5.1 |
| 9.3 | **Normal user tries to access `/api/admin/*`** | `Depends(verify_jwt)` middleware rejects — 401 response. Admin routes completely invisible to unauthenticated users. | Architecture §14.1 |
| 9.4 | **User session ID collision** (two users generate same UUID) | Extremely unlikely with random UUID v4. If it occurs, they share the same watchlist and notifications — no security impact (no PII). | Architecture §14.2 |
| 9.5 | **Rate limit exceeded on chat** (> 30 req/min) | `slowapi` returns 429 Too Many Requests. Frontend shows "Please wait" message. | Architecture §14.2 |
| 9.6 | **Rate limit exceeded on admin** (> 10 req/min) | `slowapi` returns 429. Admin sees rate-limit error. | Architecture §14.2 |
| 9.7 | **CORS request from unauthorised origin** | FastAPI CORS middleware rejects cross-origin requests not from the whitelisted frontend origin. | Architecture §14.2 |
| 9.8 | **Malicious content in scraped HTML** (XSS payloads) | Scraper extracts structured fields only via BeautifulSoup selectors — no raw HTML passed to frontend. System prompt is hardcoded (not user-modifiable). | Architecture §14.2 |

---

## 10. Frontend & WebSocket

| # | Edge Case | Expected Behaviour | Source Reference |
|---|-----------|-------------------|-----------------|
| 10.1 | **WebSocket connection drops mid-conversation** | `useWebSocket` hook implements auto-reconnect with exponential backoff. Conversation resumes on reconnect (session ID preserved). | Implementation §6.3, §7.8 |
| 10.2 | **User sends message while previous response is still streaming** | Should queue the new message or disable the send button during streaming. Implementation-dependent — recommend disabling input during stream. | Architecture §6.1 |
| 10.3 | **Very long LLM response** (exceeds viewport) | `ChatWindow` is scrollable. Auto-scroll to bottom as chunks arrive during streaming. | Architecture §13.2 |
| 10.4 | **User opens app for the first time (no session ID)** | A random UUID is generated and stored in `localStorage`. No login required. All public features immediately accessible. | Implementation §6.3 |
| 10.5 | **User clears localStorage** | Session ID is lost. New UUID generated on next visit. Watchlist and notification preferences are orphaned in the database (tied to old session_id). | Implementation §6.3 |
| 10.6 | **API timeout on REST endpoints** | Frontend shows error toast with retry button. | Implementation §7.8 |
| 10.7 | **Empty fund list for comparison** (before initial sync) | `FundSelector` shows empty dropdown. User cannot select funds. UI should show "Loading funds…" or similar empty state. | Implementation §6.5 |
| 10.8 | **Mobile layout / small screen** | Responsive CSS with stacked layout on small screens, collapsible navigation. | Implementation §7.7 |
| 10.9 | **Admin dashboard accessed without JWT** | `AuthContext` detects missing token → redirects to `/admin/login`. Dashboard content never renders. | Implementation §6.4 |
| 10.10 | **Browser tab remains open for hours** | JWT expires → next admin API call returns 401 → redirect to login. Freshness indicator continues polling and may show stale/failed status. | Architecture §14.2 |

---

## 11. Notification Subsystem

| # | Edge Case | Expected Behaviour | Source Reference |
|---|-----------|-------------------|-----------------|
| 11.1 | **Same NFO appears in consecutive scrapes without changes** | `nfo_tracking.content_hash` is identical → `is_new` remains `false`. No duplicate notification generated. | Implementation §7.5, Architecture §12.1 |
| 11.2 | **NFO disappears from Groww page** (removed/closed) | `detect_nfo_changes()` returns it in `removed_nfos`. `nfo_tracking` updated — status changes to closed/removed. No crash. | Architecture §12.1 |
| 11.3 | **User has no notification preferences set** | Default: `notify_new_nfo = false`, `notify_news = false`. No notifications generated for this user. | Architecture §5.1 (`notification_prefs` table defaults) |
| 11.4 | **User polls notifications but none exist** | `GET /api/data/notifications` returns `{ "notifications": [] }`. Frontend shows empty state. | Architecture §12.2 |
| 11.5 | **Multiple new NFOs in a single sync cycle** | Each new NFO generates a separate notification entry. All returned in the next poll. | Architecture §12.1, §12.2 |
| 11.6 | **News article title changes but content is the same** | `content_hash` of the full extracted data changes → detected as changed. May generate a redundant notification. Edge case — acceptable. | Architecture §12.1 |

---

## 12. Data Freshness & Availability

| # | Edge Case | Expected Behaviour | Source Reference |
|---|-----------|-------------------|-----------------|
| 12.1 | **All sources healthy, refreshed < 15 min ago** | `FreshnessIndicator` displays **green**. Tooltip: "All sources healthy". | Architecture §13.3 |
| 12.2 | **Some sources refreshed > 15 min ago** | `FreshnessIndicator` displays **amber**. Shows "X sources stale". | Architecture §13.3 |
| 12.3 | **Some sources in failed state** | `FreshnessIndicator` displays **red**. Shows "X sources failed". Chat still works with last-good data. | Architecture §13.3 |
| 12.4 | **No data collected yet** (fresh deployment) | `FreshnessIndicator` displays **grey** (unavailable). UI shows "Initial data loading…" with progress. | Architecture §13.3, Implementation §7.8 |
| 12.5 | **Sync in progress** | `system_state.refresh_in_progress = true`. Status API returns refresh-in-progress state. UI can show a loading spinner. | Architecture §5.1 (`system_state` table) |
| 12.6 | **Source was last successful 3 hours ago, but failed since** | `last_success_at` = 3 hours ago, `status = 'failed'`. Data is stale but still served. FreshnessIndicator shows amber/red depending on thresholds. Source citation shows the old timestamp. | Architecture §8.1 |

---

## 13. Infrastructure & Persistence

### 13.1 Database Failures

| # | Edge Case | Expected Behaviour | Source Reference |
|---|-----------|-------------------|-----------------|
| 13.1.1 | **PostgreSQL connection drops during sync** | Metadata writes fail. System should queue status updates in memory and flush on reconnect. Vectors may be written to ChromaDB but metadata not updated — creates inconsistency. Needs recovery logic. | Architecture §16.2 |
| 13.1.2 | **PostgreSQL connection drops during chat** | Chat queries that only need ChromaDB still work. Freshness queries and watchlist operations fail. Return appropriate error messages. | Architecture §16.2 |
| 13.1.3 | **Database tables not created on startup** | `init_db.py` auto-creates tables. If it fails (permissions, disk), backend cannot start. | Implementation §1.3 |
| 13.1.4 | **Seed admin user already exists on restart** | `init_db.py` should use `INSERT ... ON CONFLICT DO NOTHING` or equivalent. No duplicate admin rows. | Implementation §1.3 |

### 13.2 ChromaDB Failures

| # | Edge Case | Expected Behaviour | Source Reference |
|---|-----------|-------------------|-----------------|
| 13.2.1 | **ChromaDB write fails during vector upsert** | System retries once. If still fails, error is logged and previous vector state is retained. | Architecture §16.2 |
| 13.2.2 | **ChromaDB persistent storage corrupted** | Mitigated by daily backups of `chromadb/` directory. Recovery: restore from backup + trigger full manual sync. | Implementation Risk Mitigation |
| 13.2.3 | **ChromaDB disk space exhausted** | Write operations fail. All sources enter FAILED path until space is freed. Old vectors remain readable. | Derived |
| 13.2.4 | **Collection accidentally deleted** | On next sync cycle, embedder recreates the collection. All sources treated as NEW (no existing vectors to compare). Full re-scrape and re-embed triggered. | Implementation §3.1 |

### 13.3 Snapshot Storage

| # | Edge Case | Expected Behaviour | Source Reference |
|---|-----------|-------------------|-----------------|
| 13.3.1 | **Snapshot directory doesn't exist** | `SnapshotManager` creates it. `os.makedirs()` with `exist_ok=True`. | Implementation §3.4 |
| 13.3.2 | **`previous.json` doesn't exist (first scrape)** | No diff computed. `diff.json` not created. Change queries for this source return "No previous data available for comparison". | Implementation §3.4 |
| 13.3.3 | **Snapshot file is corrupted JSON** | `SnapshotManager.get_diff()` fails to parse. Should catch `json.JSONDecodeError`, log error, and treat as NEW source (full re-scrape). | Derived |
| 13.3.4 | **Disk full — cannot write snapshot** | Snapshot save fails. Source vectors may be updated in ChromaDB but diff tracking is lost. Log error. Non-critical — chat still works. | Derived |

---

## 14. Deployment & Environment

| # | Edge Case | Expected Behaviour | Source Reference |
|---|-----------|-------------------|-----------------|
| 14.1 | **`GROK_API_KEY` environment variable not set** | `config.py` (Pydantic Settings) raises validation error at startup. Backend refuses to start with clear error message. | Architecture §15.2, Implementation §1.2 |
| 14.2 | **`DATABASE_URL` points to unreachable PostgreSQL** | Backend startup fails during `init_database()`. FastAPI never starts serving. | Implementation §1.4 |
| 14.3 | **ChromaDB persist directory has wrong permissions** | ChromaDB initialisation fails. Backend cannot create collection. Startup error. | Implementation §3.1 |
| 14.4 | **Port 8000 already in use** | Uvicorn fails to bind. Backend does not start. Standard OS error. | Derived |
| 14.5 | **Docker container runs out of memory** | Playwright and embedding model are memory-intensive. Container OOM-killed. Need sufficient memory allocation (recommend ≥ 4 GB). | Implementation Risk Mitigation |
| 14.6 | **Initial data load takes > 10 minutes for 33 URLs** | Expected: 5–10 minutes. UI shows progress indicator. Background task with status API. User can use the app once partial data is loaded. | Implementation §3.7 |
| 14.7 | **Frontend `VITE_API_BASE_URL` misconfigured** | All API calls fail. Frontend shows network errors on every interaction. | Architecture §15.2 |

---

## 15. Concurrency & Race Conditions

| # | Edge Case | Expected Behaviour | Source Reference |
|---|-----------|-------------------|-----------------|
| 15.1 | **Scheduler and admin trigger sync simultaneously** | `system_state.refresh_in_progress` flag prevents concurrent sync cycles. Second trigger is rejected or queued. | Architecture §11.2 |
| 15.2 | **Admin deletes a URL while sync is processing that URL** | Race condition. If delete commits first, sync may fail to write vectors (source no longer active). Should handle gracefully — sync checks `is_active` before writing. | Derived |
| 15.3 | **Multiple users chat simultaneously** | Each chat uses a separate WebSocket connection and session-specific `ConversationMemory`. ChromaDB queries are read-only and concurrent-safe. No contention. | Architecture §10.1 |
| 15.4 | **Sync cycle runs while user is actively querying** | ChromaDB supports concurrent reads and writes. User may briefly see mixed results (some sources updated, others not). Acceptable — eventual consistency within 15 minutes. | Derived |
| 15.5 | **Two admin sessions open, both managing URLs** | Both see the same URL list. Conflicting edits (e.g., both delete the same URL) handled by database constraints. Second delete returns 404 or no-op. | Derived |
| 15.6 | **Server restart during an active sync cycle** | In-progress sync is interrupted. Some sources may have updated vectors, others not. On restart, next scheduled sync cycle reconciles the state. `refresh_in_progress` should be reset to `false` on startup. | Derived |

---

## Summary: Critical Edge Cases by Priority

### 🔴 Must Handle (Data Integrity / Core Promise)

| ID | Edge Case | Why Critical |
|----|-----------|-------------|
| 3.5 | Failed scrape retains old vectors | Core fail-safe promise — scrape failure ≠ data loss |
| 6.1–6.2 | Advice request blocking | Mandatory: system must never give investment advice |
| 6.7 | Missing data fallback | Exact fallback wording is a hard requirement |
| 6.3 | Hallucination detection | Source-grounding is the core product promise |
| 3.2 | Changed source re-embedding | Ensures data freshness — the 15-min refresh contract |
| 1.1.2 | All sources fail | Graceful degradation — chat must still work |

### 🟡 Should Handle (User Experience)

| ID | Edge Case | Why Important |
|----|-----------|-------------|
| 10.1 | WebSocket disconnect | Prevents broken chat experience |
| 7.1–7.2 | Follow-up resolution | Natural conversation flow |
| 5.2.2 | Partial comparison data | User sees "N/A" not an error |
| 12.4 | First startup empty state | User is not confused by blank UI |
| 8.7 | Concurrent sync prevention | Prevents resource waste and data corruption |

### 🟢 Nice to Handle (Robustness)

| ID | Edge Case | Why Useful |
|----|-----------|----------|
| 13.3.3 | Corrupt snapshot JSON | Self-healing behaviour |
| 7.5 | Server restart clears conversation memory | Awareness for future improvement |
| 15.4 | Read-during-write consistency | Acceptable trade-off for MVP |
| 11.6 | Redundant news notification | Minor UX issue, not data integrity |

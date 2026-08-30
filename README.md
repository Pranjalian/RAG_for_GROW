# Groww Market Intelligence — RAG Chatbot

A **source-grounded RAG chatbot** that answers questions about mutual funds, NFOs, and market news using only data scraped from [Groww](https://groww.in). No hallucinations. No investment advice. Strictly factual.

## Features

- 💬 **Natural-language chat** powered by GROK LLM — grounded to Groww data only
- 🔄 **Auto-refresh every 15 minutes** — 33 mandatory Groww sources kept current
- 📊 **Fund comparison** — side-by-side factual tables, no recommendations
- 🆕 **NFO discovery** — new fund offerings surfaced with notifications
- 📰 **Market news feed** — from Groww Share Market Today
- 🛡️ **Zero advice mode** — every investment advice request is declined
- 🔒 **Admin panel** — manage scraping URLs, trigger manual syncs, monitor status

## Tech Stack

| Layer | Technology |
|-------|------------|
| LLM | GROK LLM |
| Backend | FastAPI + Python 3.11 |
| RAG | LangChain + ChromaDB |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` |
| Database | PostgreSQL 15 |
| Scraper | Playwright (headless Chromium) |
| Frontend | React 18 + Vite |

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local dev)
- Node.js 18+ (for frontend dev)

### 1. Clone & configure
```bash
git clone <repo>
cd RAG_for_GROW
cp backend/.env.example backend/.env
# Edit backend/.env and fill in GROK_API_KEY and JWT_SECRET_KEY
```

### 2. Start with Docker Compose
```bash
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### 3. Local backend dev (without Docker)
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
playwright install chromium
uvicorn app.main:app --reload
```

### 4. Local frontend dev
```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

See [`backend/.env.example`](backend/.env.example) for the full list.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | ✅ | — | PostgreSQL async connection string |
| `GROK_API_KEY` | ✅ | — | GROK LLM API key |
| `JWT_SECRET_KEY` | ✅ | — | Secret for signing admin JWTs |
| `CHROMA_PERSIST_DIR` | — | `./data/chromadb` | ChromaDB storage path |
| `SNAPSHOT_DIR` | — | `./data/snapshots` | Scrape snapshot path |
| `SCRAPE_INTERVAL_MINUTES` | — | `15` | Auto-refresh interval |
| `ADMIN_DEFAULT_USERNAME` | — | `admin` | Seed admin username |
| `ADMIN_DEFAULT_PASSWORD` | — | `admin` | Seed admin password (change in prod!) |

## Admin Access

Navigate to `http://localhost:3000/admin/login`  
Default credentials: `admin` / `admin` (**change in production**)

## Project Structure

```
RAG_for_GROW/
├── docs/                    # Architecture, implementation plan, edge cases
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app factory
│   │   ├── config.py        # Settings from env vars
│   │   ├── api/             # Route handlers
│   │   ├── models/          # ORM + Pydantic schemas
│   │   ├── db/              # Session, init, migrations
│   │   ├── scraper/         # Playwright scraper + extractors
│   │   ├── pipeline/        # Sync engine, embedder, chunker
│   │   ├── rag/             # Query classifier, retriever, generator
│   │   └── auth/            # JWT + bcrypt
│   ├── data/                # ChromaDB + snapshots (gitignored)
│   └── requirements.txt
└── frontend/
    └── src/                 # React components + pages
```

## Docs

- [Architecture](docs/architecture.md)
- [Implementation Plan](docs/implementation-plan.md)
- [Edge Cases](docs/edge_cases.md)
- [Evaluation Plan](docs/eval.md)

# AI Home Styling Platform - POC

Upload a room photo, pick a style, and get AI-generated restyled renders with shoppable IKEA furniture bundles.

## Architecture

```
frontend/ (Next.js 16)          api/ (FastAPI)              ai_pipeline/
  Upload page ──POST /upload──►  upload.py ──► storage.py   room_validator.py
  Style page  ──GET  /styles──►  styles.py                  style_renderer.py
  Loading     ──POST /generate─► generate.py ──► ARQ ──►    hotspot_mapper.py
  Gallery     ──GET  /generate/  products.py                prompts/
              ──GET  /bundles/   analytics.py
```

**Pipeline flow:** Upload image → Validate room (Google Vision) → Generate styled renders (Gemini 3.1 Flash Image) → Map product hotspots (Gemini 3 Flash) → Display gallery with shoppable products

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS 4, Zustand, React Query, Framer Motion |
| Backend | FastAPI, Python 3.13, Pydantic v2, asyncpg |
| AI Models | Gemini 3.1 Flash Image (renders), Gemini 3 Flash (hotspots), Google Cloud Vision (validation) |
| AI Gateway | OpenRouter |
| Task Queue | ARQ + Redis 7 |
| Database | PostgreSQL 15 |
| Storage | GCP Cloud Storage (bucket: `ai-home-styling-poc`, region: `europe-west1`) with local fallback |
| Infra | Docker Compose (local), CranL (production target) |

## Project Structure

```
.
├── api/                        # FastAPI backend
│   ├── app/
│   │   ├── main.py             # App entry, CORS, routers
│   │   ├── config.py           # Pydantic Settings (env-based)
│   │   ├── database.py         # asyncpg pool management
│   │   ├── models/schemas.py   # Pydantic request/response models
│   │   ├── routers/            # 5 routers: upload, styles, generate, products, analytics
│   │   ├── services/storage.py # GCS upload with local fallback
│   │   ├── workers/main.py     # ARQ worker (generate_renders_task)
│   │   └── ai_pipeline/        # AI modules (copied from ai/ for import access)
│   │       ├── room_validator.py
│   │       ├── style_renderer.py
│   │       ├── hotspot_mapper.py
│   │       └── prompts/        # Style-specific prompts (modern, minimal)
│   └── pyproject.toml
├── frontend/                   # Next.js app
│   └── src/
│       ├── app/                # 4 pages: /, /style, /loading-screen/[jobId], /gallery/[sessionId]
│       ├── components/         # ImageUploader, StyleCard, RenderProgress, HotspotOverlay, ProductCard, Providers
│       ├── lib/api.ts          # API client (7 methods)
│       ├── lib/store.ts        # Zustand store (persisted to localStorage)
│       └── types/index.ts      # TypeScript interfaces
├── data/
│   ├── seed/                   # products.json, bundles.json
│   └── scripts/seed_db.py      # DB seeding script
├── supabase/
│   └── migrations/             # PostgreSQL schema (4 tables)
├── infra/
│   ├── docker-compose.yml      # Redis + Postgres for local dev
│   └── cors.json               # GCS bucket CORS config
├── Makefile                    # Dev commands
├── .env.example                # Required environment variables
└── cranl_deploy.sh             # Production deployment script
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/upload` | Upload room photo (multipart/form-data, max 20MB) |
| GET | `/api/styles` | List available styles (modern, minimal) |
| POST | `/api/generate` | Trigger AI pipeline (returns job_id) |
| GET | `/api/generate/{job_id}` | Poll job status (queued → analyzing → rendering → mapping → completed) |
| GET | `/api/bundles/{style_id}` | Get product bundle for a style |
| GET | `/api/products/{product_id}` | Get single product details |
| POST | `/api/analytics/event` | Track user interaction events |
| GET | `/health` | Health check |

## Database Schema

4 tables in PostgreSQL:

- **products** — furniture catalog (name, category, price_sar, image_urls[], dimensions, supplier, style_tags[])
- **bundles** — curated product sets per style/budget (product_ids[], style, budget_tier)
- **sessions** — user sessions (uploaded_image_url, render_urls[], hotspots JSONB, bundle_id)
- **analytics_events** — click/interaction tracking (session_id, event_type, product_id)

Categories: `sofa, table, rug, lamp, shelf, art, pillow, other`
Suppliers: `ikea, noon`
Budget tiers: `budget, mid, premium`

## Setup

### Prerequisites

- Docker & Docker Compose
- Node.js 20+ with pnpm
- Python 3.13 with uv (`pip install uv`)
- OpenRouter API key (for Gemini models)
- Google Cloud API key (for Vision API room validation)

### 1. Clone and install

```bash
# Install all dependencies
make install
# or manually:
cd frontend && pnpm install
cd api && python -m uv sync
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and add your API keys:
#   OPENROUTER_API_KEY=sk-or-v1-...
#   GOOGLE_CLOUD_API_KEY=AIza...
```

### 3. Start infrastructure

```bash
# Start Redis + Postgres via Docker
docker compose -f infra/docker-compose.yml up -d
```

### 4. Seed the database

```bash
# Run migrations
psql postgresql://postgres:password@localhost:5433/ai_styling < supabase/migrations/20260302_init.sql

# Seed products and bundles
cd data && python scripts/seed_db.py
```

### 5. Start development servers

```bash
# Start everything (API + worker + frontend)
make dev

# Or start individually:
cd api && uvicorn app.main:app --reload --port 8000
cd api && python -m arq app.workers.main.WorkerSettings   # separate terminal
cd frontend && pnpm dev                                     # separate terminal
```

Frontend: http://localhost:3000
API: http://localhost:8000
API docs: http://localhost:8000/docs

## Current Status

### What works (verified E2E)

- Photo upload with drag-and-drop, file validation, image resizing
- Room validation via Google Cloud Vision API (rejects non-room images)
- Style selection page loading styles from API
- AI render generation via Gemini 3.1 Flash Image through OpenRouter
- Hotspot mapping via Gemini 3 Flash (detects furniture positions in renders)
- Async job processing via ARQ + Redis with status polling
- Gallery page with render carousel, interactive hotspots, product strip, bundle pricing
- Session persistence via Zustand + localStorage
- Local file storage fallback when GCS is unavailable
- GCS bucket configured (`ai-home-styling-poc` in `europe-west1`, public read, CORS set)

### Known Issues / In Progress

| Issue | Status | Details |
|-------|--------|---------|
| AI renders | Working | Gemini 3.1 Flash Image via OpenRouter. Images returned in `message.images[]` array. E2E verified — real renders generated (~130KB each, ~75s). |
| Product images | Partial | 5/29 products have real IKEA images (LACK, KALLAX, BILLY, BESTA, GLADOM). Remaining 24 have wrong fallback image due to IKEA SA redirecting discontinued product pages. Need real furniture photos or alternative source. |
| Style thumbnail images missing | Low priority | Style cards show letter placeholders (M, m) instead of preview images. |
| No authentication | By design (POC) | RLS policies are all permissive. |
| CORS set to wildcard | By design (POC) | `allow_origins=["*"]` for local development simplicity. |
| CranL deployment | Not started | `cranl_deploy.sh` exists but not tested. |

### Build & Runtime Verification

| Component | Status |
|-----------|--------|
| `frontend` builds clean | Yes (`pnpm build` passes) |
| `api` starts clean | Yes (uvicorn with --reload) |
| Docker services (Redis, Postgres) | Running on ports 6379 / 5433 |
| Database seeded | 29 products, 4 bundles (modern/minimal x mid-range) |
| ARQ worker connects | Yes (1 function: `generate_renders_task`) |
| Upload → Style → Generate → Gallery flow | Verified via browser |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `OPENROUTER_API_KEY` | Yes | OpenRouter API key for Gemini models |
| `GOOGLE_CLOUD_API_KEY` | Yes | Google Cloud API key for Vision API |
| `GCP_PROJECT_ID` | No | GCP project ID (for GCS) |
| `GCS_BUCKET` | No | GCS bucket name (falls back to local storage) |
| `REDIS_URL` | No | Redis URL (default: `redis://localhost:6379`) |
| `API_URL` | No | API base URL (default: `http://localhost:8000`) |
| `FRONTEND_URL` | No | Frontend URL (default: `http://localhost:3000`) |

## Key Design Decisions

1. **OpenRouter over Vertex AI** — simpler API key auth, no GCP service account setup for POC
2. **ARQ over Celery** — lightweight, async-native, minimal config for a POC task queue
3. **Gemini 3.1 Flash Image** — latest Gemini model for image generation via OpenRouter; images returned in `message.images[]` array
4. **Zustand over Redux** — minimal boilerplate, perfect for POC scope, persist middleware for session survival
5. **Local storage fallback** — GCS upload gracefully falls back to serving files from `/public` directory
6. **ai_pipeline copied into api/app/** — avoids Python import path issues; the `ai/` directory is the original source, `api/app/ai_pipeline/` is the runtime copy

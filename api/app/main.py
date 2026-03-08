import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db_pool, close_db_pool
from app.routers import analytics, generate, products, styles, upload

logger = logging.getLogger(__name__)


async def _init_db_with_retry(max_attempts: int = 5, delay: float = 5.0) -> None:
    for attempt in range(1, max_attempts + 1):
        try:
            await init_db_pool()
            logger.info("Database pool initialized successfully")
            await _seed_initial_data()
            return
        except Exception as exc:
            logger.warning("DB connect attempt %d/%d failed: %s", attempt, max_attempts, exc)
            if attempt < max_attempts:
                await asyncio.sleep(delay)
    logger.error("Could not connect to database after %d attempts – DB-backed endpoints will fail", max_attempts)


async def _seed_initial_data() -> None:
    """Insert starter bundles and products if the tables are empty (idempotent)."""
    from app.database import get_db_pool
    pool = get_db_pool()

    bundle_count = await pool.fetchval("SELECT COUNT(*) FROM bundles")
    if bundle_count and bundle_count > 0:
        logger.info("Seed data already present (%d bundles), skipping", bundle_count)
        return

    logger.info("Seeding initial bundles and products...")

    # Insert products first
    products = [
        # Modern style products
        ("Modern Sofa", "أريكة عصرية", "sofa", 3499.00,
         ["https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800"],
         '{"width": 220, "depth": 90, "height": 85}', "ikea",
         "https://www.ikea.com/sa/en/p/kivik-sofa-hillared-anthracite/",
         ["modern", "contemporary"]),
        ("Marble Coffee Table", "طاولة قهوة رخامية", "table", 1299.00,
         ["https://images.unsplash.com/photo-1611269154421-4e27233ac5c7?w=800"],
         '{"width": 120, "depth": 60, "height": 45}', "west elm",
         "https://www.westelm.com/products/marble-topped-brass-coffee-table/",
         ["modern", "luxury"]),
        ("Geometric Area Rug", "سجادة هندسية", "rug", 899.00,
         ["https://images.unsplash.com/photo-1575414003765-e7c26c4e78cd?w=800"],
         '{"width": 200, "depth": 300, "height": 1}', "noon",
         "https://www.noon.com/saudi-en/geometric-rug/",
         ["modern", "geometric"]),
        ("Arc Floor Lamp", "مصباح أرضي", "lamp", 499.00,
         ["https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=800"],
         '{"width": 30, "depth": 30, "height": 180}', "ikea",
         "https://www.ikea.com/sa/en/p/hektar-floor-lamp/",
         ["modern", "industrial"]),
        # Minimal style products
        ("Low-Profile Sofa", "أريكة منخفضة", "sofa", 2799.00,
         ["https://images.unsplash.com/photo-1567538096630-e0c55bd6374c?w=800"],
         '{"width": 200, "depth": 85, "height": 70}', "ikea",
         "https://www.ikea.com/sa/en/p/gronlid-sofa/",
         ["minimal", "scandinavian"]),
        ("Natural Wood Side Table", "طاولة جانبية خشبية", "table", 649.00,
         ["https://images.unsplash.com/photo-1594026112334-d8040bd05726?w=800"],
         '{"width": 50, "depth": 50, "height": 55}', "west elm",
         "https://www.westelm.com/products/wood-side-table/",
         ["minimal", "natural"]),
        ("Neutral Wool Rug", "سجادة صوف محايدة", "rug", 1199.00,
         ["https://images.unsplash.com/photo-1600166898405-da9535204843?w=800"],
         '{"width": 160, "depth": 230, "height": 1}', "noon",
         "https://www.noon.com/saudi-en/wool-rug/",
         ["minimal", "natural"]),
        ("Simple Pendant Light", "مصباح معلق بسيط", "lamp", 349.00,
         ["https://images.unsplash.com/photo-1540932239986-30128078f3c5?w=800"],
         '{"width": 25, "depth": 25, "height": 40}', "ikea",
         "https://www.ikea.com/sa/en/p/nymane-pendant-lamp/",
         ["minimal", "scandinavian"]),
    ]

    product_ids = []
    for (name, name_ar, category, price, image_urls, dims, supplier, url, tags) in products:
        pid = await pool.fetchval(
            """INSERT INTO products
               (name, name_ar, category, price_sar, image_urls, dimensions_cm, supplier, product_url, style_tags)
               VALUES ($1, $2, $3, $4, $5, $6::jsonb, $7, $8, $9)
               RETURNING id""",
            name, name_ar, category, price, image_urls, dims, supplier, url, tags,
        )
        product_ids.append((pid, tags))
        logger.info("Seeded product: %s (id=%s)", name, pid)

    modern_ids = [pid for pid, tags in product_ids if "modern" in tags]
    minimal_ids = [pid for pid, tags in product_ids if "minimal" in tags]

    for style, name, ids in [
        ("modern", "Modern Living Bundle", modern_ids),
        ("minimal", "Minimal Living Bundle", minimal_ids),
    ]:
        bid = await pool.fetchval(
            """INSERT INTO bundles (name, style, budget_tier, product_ids)
               VALUES ($1, $2, $3, $4)
               RETURNING id""",
            name, style, "mid", ids,
        )
        logger.info("Seeded bundle: %s (id=%s, %d products)", name, bid, len(ids))

    logger.info("Seed complete")


PUBLIC_DIR = Path(__file__).parent.parent / "public"
PUBLIC_DIR.mkdir(exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Try to connect to the DB but don't crash the process if it's unreachable.
    # This keeps /health alive while the DB warms up or is being provisioned.
    asyncio.ensure_future(_init_db_with_retry())

    yield

    await close_db_pool()


app = FastAPI(
    title="AI Home Styling Platform",
    description="POC API for AI-powered interior design styling",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/public", StaticFiles(directory=str(PUBLIC_DIR)), name="public")

app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(styles.router, prefix="/api", tags=["Styles"])
app.include_router(generate.router, prefix="/api", tags=["Generate"])
app.include_router(products.router, prefix="/api", tags=["Products"])
app.include_router(analytics.router, prefix="/api", tags=["Analytics"])


@app.get("/")
async def root():
    return {"status": "ok", "message": "AI Home Styling API"}


@app.get("/health")
async def health():
    return {"status": "ok"}

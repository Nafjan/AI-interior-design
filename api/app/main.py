from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db_pool, close_db_pool
from app.routers import analytics, generate, products, styles, upload


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Path("public").mkdir(exist_ok=True)
    await init_db_pool()
    yield
    # Shutdown
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

app.mount("/public", StaticFiles(directory="public"), name="public")

app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(styles.router, prefix="/api", tags=["Styles"])
app.include_router(generate.router, prefix="/api", tags=["Generate"])
app.include_router(products.router, prefix="/api", tags=["Products"])
app.include_router(analytics.router, prefix="/api", tags=["Analytics"])


@app.get("/health")
async def health():
    return {"status": "ok"}

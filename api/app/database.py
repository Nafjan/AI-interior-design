import asyncpg
from app.config import settings

_pool: asyncpg.Pool | None = None

async def init_db_pool():
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(dsn=settings.database_url)

async def close_db_pool():
    global _pool
    if _pool is not None:
        await _pool.close()

def get_db_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("Database pool is not initialized")
    return _pool

import json
import logging
from typing import Any

from arq.connections import RedisSettings
from redis.asyncio import Redis

from app.config import settings
from app.database import init_db_pool, close_db_pool

logger = logging.getLogger(__name__)

async def startup(ctx: dict[str, Any]) -> None:
    """Initialize resources on worker startup."""
    await init_db_pool()
    ctx["redis"] = Redis.from_url(settings.redis_url, decode_responses=True)
    logger.info("Worker started.")

async def shutdown(ctx: dict[str, Any]) -> None:
    """Cleanup resources on worker shutdown."""
    await close_db_pool()
    await ctx["redis"].close()
    logger.info("Worker shutdown.")

async def set_job_status(redis: Redis, job_id: str, status: dict[str, Any]) -> None:
    """Update job status in Redis."""
    await redis.set(f"job:{job_id}:status", json.dumps(status), ex=3600)

async def generate_renders_task(ctx: dict[str, Any], job_id: str, session_id: str, style_id: str) -> None:
    """ARQ task to run the generation pipeline."""
    # We will implement the actual AI pipeline later (Phase 7).
    # For now, this is a placeholder that updates status.
    redis: Redis = ctx["redis"]
    
    try:
        await set_job_status(redis, job_id, {"job_id": job_id, "status": "analyzing", "progress": "Analyzing your room..."})
        
        # Placeholder for real pipeline logic...
        # Import and run _run_pipeline logic here, updated to use set_job_status.
        from app.routers.generate import _run_pipeline_impl
        await _run_pipeline_impl(job_id, session_id, style_id, redis)
        
    except Exception as e:
        logger.exception("Task failed: %s", e)
        await set_job_status(redis, job_id, {"job_id": job_id, "status": "failed", "error": str(e)})

class WorkerSettings:
    functions = [generate_renders_task]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(settings.redis_url)

import json
import logging

from fastapi import APIRouter

from app.database import get_db_pool
from app.models.schemas import AnalyticsEvent

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/analytics/event")
async def log_event(event: AnalyticsEvent):
    pool = get_db_pool()

    try:
        query = """
            INSERT INTO analytics_events (session_id, event_type, product_id, metadata)
            VALUES ($1, $2, $3, $4)
        """
        await pool.execute(
            query,
            event.session_id,
            event.event_type,
            event.product_id,
            json.dumps(event.metadata or {})
        )
    except Exception as e:
        logger.warning("Failed to log analytics event: %s", e)

    return {"ok": True}

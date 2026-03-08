"""GCP Cloud Storage service for uploads and renders.

For POC without GCS configured, falls back to local file storage.
"""

import io
import logging
import uuid
from pathlib import Path

from PIL import Image

from app.config import settings

logger = logging.getLogger(__name__)

MAX_DIMENSION = 2048

_gcs_client = None


def _get_gcs_client():
    global _gcs_client
    if _gcs_client is not None:
        return _gcs_client
    if not settings.gcs_bucket:
        return None
    try:
        from google.cloud import storage
        _gcs_client = storage.Client(project=settings.gcp_project_id or None)
        return _gcs_client
    except Exception as e:
        logger.warning("Could not initialize GCS client: %s", e)
        return None


def _resize_image(image_bytes: bytes, max_dim: int = MAX_DIMENSION) -> bytes:
    """Resize image if larger than max_dim, preserving aspect ratio."""
    img = Image.open(io.BytesIO(image_bytes))
    if max(img.size) > max_dim:
        img.thumbnail((max_dim, max_dim), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def upload_image(file_bytes: bytes, folder: str = "uploads", extension: str = "jpg") -> str:
    """Upload image bytes to storage. Returns the public URL."""
    resized = _resize_image(file_bytes)
    filename = f"{folder}/{uuid.uuid4()}.{extension}"

    client = _get_gcs_client()
    if client:
        try:
            bucket = client.bucket(settings.gcs_bucket)
            blob = bucket.blob(filename)
            blob.upload_from_string(resized, content_type=f"image/{extension}")
            return f"https://storage.googleapis.com/{settings.gcs_bucket}/{filename}"
        except Exception as e:
            logger.warning("GCS upload failed, falling back to local: %s", e)

    # Fallback: use local storage for dev
    upload_dir = Path("public") / folder
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = Path("public") / filename
    with open(file_path, "wb") as f:
        f.write(resized)

    return f"{settings.api_url}/public/{filename}"


def upload_render(image_bytes: bytes, session_id: str, variant: int) -> str:
    """Upload a generated render image."""
    return upload_image(image_bytes, folder=f"renders/{session_id}", extension="jpg")

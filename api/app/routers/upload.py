from fastapi import APIRouter, File, HTTPException, UploadFile

from app.database import get_db_pool
from app.models.schemas import UploadResponse
from app.services.storage import upload_image

router = APIRouter()

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/heic"}
MAX_SIZE_MB = 20


@router.post("/upload", response_model=UploadResponse)
async def upload_room_photo(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Accepted: JPEG, PNG, WebP, HEIC.",
        )

    contents = await file.read()
    if len(contents) > MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File too large. Max {MAX_SIZE_MB}MB.")

    # Upload to storage
    image_url = upload_image(contents)

    # Create session in database
    pool = get_db_pool()
    query = """
        INSERT INTO sessions (uploaded_image_url, room_type)
        VALUES ($1, $2)
        RETURNING id, created_at
    """
    row = await pool.fetchrow(query, image_url, "living_room")

    return UploadResponse(
        session_id=row["id"],
        image_url=image_url,
        room_type="living_room",
        created_at=row["created_at"],
    )

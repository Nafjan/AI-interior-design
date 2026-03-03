from fastapi import APIRouter

from app.models.schemas import StyleResponse

router = APIRouter()

# Hardcoded styles for the POC (Modern + Minimal only)
STYLES = [
    StyleResponse(
        id="modern",
        name="Modern",
        description="Clean lines, neutral palette with warm accents, natural materials, minimal clutter.",
        thumbnail_url="https://images.unsplash.com/photo-1583847268964-b28dc8f51f92?auto=format&fit=crop&w=600&q=80",
    ),
    StyleResponse(
        id="minimal",
        name="Minimal",
        description="Simplicity and function, muted tones, open space, carefully curated essentials.",
        thumbnail_url="https://images.unsplash.com/photo-1600607686527-6fb886090705?auto=format&fit=crop&w=600&q=80",
    ),
]


@router.get("/styles", response_model=list[StyleResponse])
async def get_styles():
    return STYLES

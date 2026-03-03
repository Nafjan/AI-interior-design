from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


# --- Upload ---

class UploadResponse(BaseModel):
    session_id: UUID
    image_url: str
    room_type: str | None = None
    created_at: datetime


# --- Styles ---

class StyleResponse(BaseModel):
    id: str
    name: str
    description: str
    thumbnail_url: str


# --- Generate ---

class GenerateRequest(BaseModel):
    session_id: UUID
    style_id: str


class GenerateResponse(BaseModel):
    job_id: str
    status: str = "queued"


class Hotspot(BaseModel):
    product_id: UUID
    x_pct: float
    y_pct: float
    category: str


class RenderResult(BaseModel):
    url: str
    hotspots: list[Hotspot]


class JobStatus(BaseModel):
    job_id: str
    status: str  # queued | analyzing | rendering | mapping | completed | failed
    progress: str | None = None
    renders: list[RenderResult] | None = None
    bundle_id: UUID | None = None
    error: str | None = None


# --- Products ---

class ProductSummary(BaseModel):
    id: UUID
    name: str
    category: str
    price_sar: Decimal
    image_url: str
    supplier: str
    product_url: str


class Product(BaseModel):
    id: UUID
    name: str
    name_ar: str | None = None
    category: str
    price_sar: Decimal
    image_urls: list[str]
    dimensions_cm: dict | None = None
    supplier: str
    product_url: str
    style_tags: list[str]


class ProductBundle(BaseModel):
    id: UUID
    name: str
    style: str
    budget_tier: str
    products: list[ProductSummary]
    total_price_sar: Decimal


# --- Analytics ---

class AnalyticsEvent(BaseModel):
    session_id: UUID
    event_type: str
    product_id: UUID | None = None
    metadata: dict | None = None

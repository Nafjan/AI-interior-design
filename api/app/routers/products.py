from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.database import get_db_pool
from app.models.schemas import Product, ProductBundle, ProductSummary

router = APIRouter()


@router.get("/bundles/{style_id}", response_model=ProductBundle)
async def get_bundle(style_id: str):
    pool = get_db_pool()

    bundle = await pool.fetchrow("SELECT * FROM bundles WHERE style = $1 LIMIT 1", style_id)
    if not bundle:
        raise HTTPException(status_code=404, detail=f"No bundle found for style: {style_id}")

    product_ids = bundle["product_ids"]

    if product_ids:
        products = await pool.fetch("SELECT * FROM products WHERE id = ANY($1::uuid[])", product_ids)
    else:
        products = []

    product_summaries = [
        ProductSummary(
            id=p["id"],
            name=p["name"],
            category=p["category"],
            price_sar=Decimal(str(p["price_sar"])),
            image_url=p["image_urls"][0] if p["image_urls"] else "",
            supplier=p["supplier"],
            product_url=p["product_url"],
        )
        for p in products
    ]

    total = sum(Decimal(str(p["price_sar"])) for p in products)

    return ProductBundle(
        id=bundle["id"],
        name=bundle["name"],
        style=bundle["style"],
        budget_tier=bundle["budget_tier"],
        products=product_summaries,
        total_price_sar=total,
    )


@router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: UUID):
    pool = get_db_pool()
    p = await pool.fetchrow("SELECT * FROM products WHERE id = $1 LIMIT 1", product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")

    return Product(
        id=p["id"],
        name=p["name"],
        name_ar=p.get("name_ar"),
        category=p["category"],
        price_sar=Decimal(str(p["price_sar"])),
        image_urls=p["image_urls"],
        dimensions_cm=p.get("dimensions_cm"),
        supplier=p["supplier"],
        product_url=p["product_url"],
        style_tags=p["style_tags"],
    )

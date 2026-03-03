"""Map furniture hotspots on generated renders using Gemini text model via OpenRouter."""

import base64
import json
import logging
import re

import httpx

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
# Use Gemini 3 Flash for fast text analysis
ANALYSIS_MODEL = "google/gemini-3-flash-preview"

HOTSPOT_PROMPT = """You are an expert interior design data extractor.
Analyze this interior design render image and identify the exact location of each major piece of furniture visible in the room.

For each furniture item, you must provide:
- category: one of (sofa, table, rug, lamp, shelf, art, pillow, other)
- x_pct: the horizontal position of the exact VISUAL CENTER of the item, as a percentage from the left edge (0.0 to 100.0)
- y_pct: the vertical position of the exact VISUAL CENTER of the item, as a percentage from the top edge (0.0 to 100.0)
- description: brief description of the item (e.g. "3-seat beige sofa")

CRITICAL INSTRUCTIONS:
- Return ONLY a raw JSON array.
- Do NOT include any markdown formatting like ```json
- Do NOT include any conversational text.
- Be precise with the coordinates using decimal points.

Example valid output:
[
  {"category": "sofa", "x_pct": 50.5, "y_pct": 60.2, "description": "3-seat beige sofa"},
  {"category": "table", "x_pct": 45.0, "y_pct": 70.0, "description": "wooden coffee table"}
]"""


async def map_hotspots(
    api_key: str,
    render_image_bytes: bytes,
    bundle_products: list[dict],
) -> list[dict]:
    """Detect furniture positions in a render and map them to bundle products.

    Returns a list of hotspot dicts: {product_id, x_pct, y_pct, category}
    """
    b64 = base64.b64encode(render_image_bytes).decode()

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                OPENROUTER_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "HTTP-Referer": "https://ai-home-styling.com",
                    "X-Title": "AI Home Styling Platform",
                },
                json={
                    "model": ANALYSIS_MODEL,
                    "messages": [{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": HOTSPOT_PROMPT},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                            },
                        ],
                    }],
                },
            )
            response.raise_for_status()
            data = response.json()

            text = data["choices"][0]["message"]["content"]

            # Extract JSON from the response (handle markdown code blocks)
            json_match = re.search(r"\[.*\]", text, re.DOTALL)
            if not json_match:
                logger.warning("No JSON array found in hotspot response: %s", text[:300])
                return _fallback_hotspots(bundle_products)

            detected = json.loads(json_match.group())

        except Exception as e:
            logger.error("Hotspot mapping failed: %s", e)
            return _fallback_hotspots(bundle_products)

    # Match detected items to bundle products by category
    return _match_to_products(detected, bundle_products)


def _match_to_products(detected: list[dict], products: list[dict]) -> list[dict]:
    """Match detected furniture items to actual bundle products by category."""
    hotspots = []
    used_product_ids = set()

    # Build category -> products mapping
    category_products = {}
    for p in products:
        cat = p.get("category", "other")
        if cat not in category_products:
            category_products[cat] = []
        category_products[cat].append(p)

    for item in detected:
        category = item.get("category", "other")
        x = item.get("x_pct", 50)
        y = item.get("y_pct", 50)
        
        # Normalize coordinates if they are > 100 (some models return pixel coordinates instead of percentages)
        if x > 100:
            x = (x / 1000) * 100 if x > 1000 else (x / 100)
        if y > 100:
            y = (y / 1000) * 100 if y > 1000 else (y / 100)
            
        # Ensure they are within 0-100 bounds
        x = max(0, min(100, x))
        y = max(0, min(100, y))

        # Find a matching product we haven't used yet
        candidates = category_products.get(category, [])
        matched_product = None
        for p in candidates:
            if p["id"] not in used_product_ids:
                matched_product = p
                used_product_ids.add(p["id"])
                break

        if not matched_product and candidates:
            matched_product = candidates[0]

        if matched_product:
            hotspots.append({
                "product_id": matched_product["id"],
                "x_pct": float(x),
                "y_pct": float(y),
                "category": category,
            })

    return hotspots


def _fallback_hotspots(products: list[dict]) -> list[dict]:
    """Generate fallback hotspot positions in a grid layout."""
    hotspots = []
    positions = [
        (30, 55), (50, 50), (70, 55),  # Middle row
        (25, 70), (50, 70), (75, 70),  # Lower row
        (40, 30), (60, 30),            # Upper row
    ]

    for i, product in enumerate(products[:8]):
        x, y = positions[i % len(positions)]
        hotspots.append({
            "product_id": product["id"],
            "x_pct": float(x),
            "y_pct": float(y),
            "category": product.get("category", "other"),
        })

    return hotspots

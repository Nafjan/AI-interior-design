"""Fetch real product images from IKEA product pages."""

import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import httpx

PRODUCTS_FILE = Path(__file__).parent.parent / "seed" / "products.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def extract_image_url(html: str, product_url: str) -> str | None:
    """Extract the main product image URL from IKEA page HTML."""

    # Method 1: og:image meta tag
    og_match = re.search(r'<meta\s+property=["\']og:image["\']\s+content=["\']([^"\']+)["\']', html)
    if not og_match:
        og_match = re.search(r'<meta\s+content=["\']([^"\']+)["\']\s+property=["\']og:image["\']', html)
    if og_match:
        url = og_match.group(1)
        if "ikea.com" in url and "images/products" in url:
            return url

    # Method 2: Look for product image in __NEXT_DATA__ or embedded JSON
    next_data_match = re.search(r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
    if next_data_match:
        try:
            data = json.loads(next_data_match.group(1))
            # Try to navigate to product image in Next.js data
            images = _find_images_in_dict(data)
            for img in images:
                if "ikea.com" in img and "images/products" in img:
                    return img
        except json.JSONDecodeError:
            pass

    # Method 3: Look for product image URLs in the HTML
    img_matches = re.findall(r'https://www\.ikea\.com/[^"\']+/images/products/[^"\']+_s5\.jpg[^"\']*', html)
    if img_matches:
        return img_matches[0].split("?")[0]  # Remove query params

    # Method 4: Any IKEA product image
    img_matches = re.findall(r'https://www\.ikea\.com/[^"\']+/images/products/[^"\']+\.jpg[^"\']*', html)
    if img_matches:
        # Prefer _s5 size
        for m in img_matches:
            if "_s5" in m:
                return m.split("?")[0]
        return img_matches[0].split("?")[0]

    return None


def _find_images_in_dict(obj, depth=0) -> list[str]:
    """Recursively find image URLs in a nested dict/list."""
    if depth > 10:
        return []
    images = []
    if isinstance(obj, dict):
        for key, val in obj.items():
            if isinstance(val, str) and "images/products" in val and val.startswith("http"):
                images.append(val)
            else:
                images.extend(_find_images_in_dict(val, depth + 1))
    elif isinstance(obj, list):
        for item in obj:
            images.extend(_find_images_in_dict(item, depth + 1))
    return images


def main():
    with open(PRODUCTS_FILE) as f:
        products = json.load(f)

    updated = 0
    failed = []

    with httpx.Client(headers=HEADERS, follow_redirects=True, timeout=15.0) as client:
        for i, product in enumerate(products):
            product_url = product.get("product_url", "")
            name = product["name"]

            # Skip generic URLs
            if not product_url or product_url.endswith("/sa/en/") or "placehold" in product_url:
                print(f"  [{i+1}/29] SKIP {name} - no valid product URL")
                failed.append(name)
                continue

            print(f"  [{i+1}/29] Fetching {name}...", end=" ", flush=True)

            try:
                resp = client.get(product_url)
                if resp.status_code == 200:
                    img_url = extract_image_url(resp.text, product_url)
                    if img_url:
                        product["image_urls"] = [img_url]
                        updated += 1
                        print(f"OK -> {img_url[:80]}...")
                    else:
                        print("NO IMAGE FOUND in HTML")
                        failed.append(name)
                else:
                    print(f"HTTP {resp.status_code}")
                    failed.append(name)
            except Exception as e:
                print(f"ERROR: {e}")
                failed.append(name)

            time.sleep(0.5)  # Be polite

    # Save updated products
    with open(PRODUCTS_FILE, "w") as f:
        json.dump(products, f, indent=2, ensure_ascii=False)

    print(f"\nDone: {updated}/29 products updated")
    if failed:
        print(f"Failed ({len(failed)}): {', '.join(failed)}")


if __name__ == "__main__":
    main()

import asyncio
import os
import httpx
from pathlib import Path
from dotenv import load_dotenv
import psycopg
import sys
import io

# Fix windows encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

root = Path(__file__).parent.parent.parent
load_dotenv(root / ".env")
DATABASE_URL = os.environ.get("DATABASE_URL")

async def check_links():
    print(f"Connecting to database...")
    
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, supplier, product_url, image_urls FROM products;")
            products = cur.fetchall()
            
    print(f"Found {len(products)} products in the database.")
    
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True, headers={"User-Agent": "Mozilla/5.0"}) as client:
        for p in products:
            pid, name, supplier, url, images = p
            print(f"\nChecking: {name} ({supplier})")
            print(f"URL: {url}")
            
            # Check product url
            try:
                resp = await client.head(url)
                print(f"  -> Product URL Status: {resp.status_code}")
                if resp.status_code >= 400:
                    print(f"  -> ERROR: Invalid product URL!")
            except Exception as e:
                print(f"  -> ERROR: Request failed: {e}")
                
            # Check image url
            if images:
                img_url = images[0]
                try:
                    resp = await client.head(img_url)
                    print(f"  -> Image URL Status: {resp.status_code}")
                except Exception as e:
                    print(f"  -> ERROR: Image request failed: {e}")
            else:
                print("  -> ERROR: No image URL!")

if __name__ == "__main__":
    asyncio.run(check_links())

"""Seed the Postgres database with products and bundles."""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
import psycopg

# Load env from project root
root = Path(__file__).parent.parent.parent
load_dotenv(root / ".env")

DATABASE_URL = os.environ.get("DATABASE_URL")

seed_dir = Path(__file__).parent.parent / "seed"


def seed_products(conn):
    """Insert products and return a name->id mapping."""
    with open(seed_dir / "products.json", encoding="utf-8") as f:
        products = json.load(f)

    with conn.cursor() as cur:
        # Clear existing
        cur.execute("TRUNCATE TABLE products CASCADE")

        print(f"Inserting {len(products)} products...")
        name_to_id = {}
        for p in products:
            cur.execute("""
                INSERT INTO products (name, name_ar, category, price_sar, image_urls, dimensions_cm, supplier, product_url, style_tags)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                p["name"],
                p.get("name_ar"),
                p["category"],
                p["price_sar"],
                p.get("image_urls", []),
                json.dumps(p.get("dimensions_cm")) if p.get("dimensions_cm") else None,
                p["supplier"],
                p["product_url"],
                p.get("style_tags", [])
            ))
            pid = cur.fetchone()[0]
            name_to_id[p["name"]] = pid

        conn.commit()

    print(f"  Inserted {len(products)} products")
    return name_to_id


def seed_bundles(conn, name_to_id: dict):
    """Insert bundles, resolving product names to IDs."""
    with open(seed_dir / "bundles.json", encoding="utf-8") as f:
        bundles = json.load(f)

    with conn.cursor() as cur:
        # Clear existing
        cur.execute("TRUNCATE TABLE bundles CASCADE")

        rows = []
        for bundle in bundles:
            product_ids = []
            for name in bundle["product_names"]:
                pid = name_to_id.get(name)
                if pid:
                    product_ids.append(pid)
                else:
                    print(f"  WARNING: product '{name}' not found, skipping")

            cur.execute("""
                INSERT INTO bundles (name, style, budget_tier, product_ids)
                VALUES (%s, %s, %s, %s)
            """, (
                bundle["name"],
                bundle["style"],
                bundle["budget_tier"],
                product_ids
            ))
            rows.append(bundle)

        conn.commit()

    print(f"Inserting {len(rows)} bundles...")
    print(f"  Inserted {len(rows)} bundles")


def main():
    print("=== Seeding database ===")
    if not DATABASE_URL:
        print("DATABASE_URL not set!")
        sys.exit(1)

    print(f"Connecting to Postgres...")
    with psycopg.connect(DATABASE_URL) as conn:
        name_to_id = seed_products(conn)
        seed_bundles(conn, name_to_id)
        
    print("=== Done ===")


if __name__ == "__main__":
    main()

import json
from pathlib import Path

products_file = Path(__file__).parent.parent / "seed" / "products.json"

with open(products_file, "r", encoding="utf-8") as f:
    products = json.load(f)

# Fallback image mapping per category
FALLBACK_IMAGES = {
    "sofa": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=400&q=80",
    "table": "https://images.unsplash.com/photo-1533090481720-856c6e3c1fdc?auto=format&fit=crop&w=400&q=80",
    "rug": "https://images.unsplash.com/photo-1622372738946-62e02505feb3?auto=format&fit=crop&w=400&q=80",
    "lamp": "https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?auto=format&fit=crop&w=400&q=80",
    "shelf": "https://images.unsplash.com/photo-1594620302200-9a762244a156?auto=format&fit=crop&w=400&q=80",
    "art": "https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?auto=format&fit=crop&w=400&q=80",
    "pillow": "https://images.unsplash.com/photo-1584100936595-c0654b55a2e6?auto=format&fit=crop&w=400&q=80",
    "other": "https://images.unsplash.com/photo-1538688525198-9b88f6f53126?auto=format&fit=crop&w=400&q=80"
}

BAD_IMAGES = [
    "https://www.ikea.com/gb/en/images/products/dyvlinge-swivel-easy-chair-kelinge-orange__1322501_pe942192_s5.jpg",
    "https://www.alrugaibfurniture.com/cdn/shop/files/1_bc54c0e6-a0f1-43cb-b09e-7111fcaf59f0.png?v=1708849767&width=800",
    "https://www.alrugaibfurniture.com/cdn/shop/files/1_1_2112e58a-356c-4860-93cb-b70d473456bb.jpg?v=1705307775&width=800",
    "https://www.alrugaibfurniture.com/cdn/shop/files/1_0769cf31-df1f-4a00-bb67-6a6d6f22e8db.png?v=1706686307&width=800",
    "https://www.alrugaibfurniture.com/cdn/shop/files/1_f32c3f86-cf5d-4fbc-b873-4f9e160a0fb4.png?v=1705822363&width=800"
]

ALRUGAIB_UPDATES = {
    "أريكة استرخاء 3 مقاعد - بورتلاند": {
        "url": "https://www.alrugaibfurniture.com/ar/collections/sofas/products/rouge-sofa",
        "img": "https://www.alrugaibfurniture.com/cdn/shop/files/elif-rosy-sofa-221cm-5692430.png?v=1769237049"
    },
    "طاولة قهوة دائرية رخام - ماربل": {
        "url": "https://www.alrugaibfurniture.com/ar/collections/coffee-tables/products/hardy-occasional-coffee-table",
        "img": "https://www.alrugaibfurniture.com/cdn/shop/files/hardy-occasional-coffee-table-3598668.png?v=1770541692"
    }
}

for p in products:
    # Update Al Rugaib dead products
    if p["name"] in ALRUGAIB_UPDATES:
        p["product_url"] = ALRUGAIB_UPDATES[p["name"]]["url"]
        p["image_urls"] = [ALRUGAIB_UPDATES[p["name"]]["img"]]
    
    # Replace orange chairs and other dead links with nice category fallbacks
    elif not p.get("image_urls") or any(bad in p["image_urls"][0] for bad in BAD_IMAGES) or p["image_urls"][0].startswith("https://placehold.co"):
        p["image_urls"] = [FALLBACK_IMAGES.get(p["category"], FALLBACK_IMAGES["other"])]

with open(products_file, "w", encoding="utf-8") as f:
    json.dump(products, f, indent=2, ensure_ascii=False)
    
print("Fixed products.json images and URLs!")

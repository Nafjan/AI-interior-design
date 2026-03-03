import json
from pathlib import Path

products_file = Path(__file__).parent.parent / "seed" / "products.json"
with open(products_file, "r", encoding="utf-8") as f:
    products = json.load(f)

# Deduplicate based on name
seen = set()
deduped = []
for p in products:
    if p["name"] not in seen:
        seen.add(p["name"])
        deduped.append(p)

with open(products_file, "w", encoding="utf-8") as f:
    json.dump(deduped, f, indent=2, ensure_ascii=False)
    
print(f"Deduplicated products from {len(products)} down to {len(deduped)}.")

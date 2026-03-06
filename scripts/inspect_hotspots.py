import os
import json

files = {
    "Balkán": "balkan-security-map/docs/data/hotspots.json",
    "Közép- és Kelet-Európa": "cee-security-map/data/hotspots.json"
}

for region, path in files.items():

    print(f"\n=== {region} ===")

    if not os.path.exists(path):
        print("hotspots.json NOT FOUND")
        continue

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("Generated:", data.get("generated_utc"))

    hotspots = data.get("top", [])

    print("Hotspot count:", len(hotspots))
    print()

    for h in hotspots[:5]:
        print(h)

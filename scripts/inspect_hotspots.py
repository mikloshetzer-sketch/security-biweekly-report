import os
import json

files = {
    "Balkán": "balkan-security-map/docs/data/hotspots.json",
    "Közép- és Kelet-Európa": "cee-security-map/data/hotspots.json"
}

for region, path in files.items():
    print(f"=== {region} ===")

    if not os.path.exists(path):
        print("hotspots.json NOT FOUND")
        print()
        continue

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("File found")

    if isinstance(data, list):
        print("Type: list")
        print("Items:", len(data))
        if len(data) > 0:
            first = data[0]
            print("First item keys:", list(first.keys()) if isinstance(first, dict) else type(first))
            print("First item:", first)
    elif isinstance(data, dict):
        print("Type: dict")
        print("Keys:", list(data.keys()))
        for key, value in data.items():
            print(f"Sample from key: {key}")
            print(value)
            break
    else:
        print("Unknown type:", type(data))

    print()

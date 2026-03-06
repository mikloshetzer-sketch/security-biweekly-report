import os
import json

files = {
    "Balkán": "balkan-security-map/docs/data/weekly.json",
    "Közép- és Kelet-Európa": "cee-security-map/data/weekly.json"
}

for region, path in files.items():
    print(f"=== {region} ===")

    if not os.path.exists(path):
        print("weekly.json NOT FOUND")
        print()
        continue

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("Type:", type(data).__name__)

    if isinstance(data, dict):
        print("Keys:", list(data.keys()))
        for key, value in data.items():
            print("Sample key:", key)
            print("Sample value type:", type(value).__name__)
            print("Sample value:", value)
            break

    elif isinstance(data, list):
        print("Items:", len(data))
        if data:
            print("First item:", data[0])

    print()

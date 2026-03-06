import os
import json

path = "me-security-monitor/events.json"

print("=== Middle East events.json inspection ===")
print()

if not os.path.exists(path):
    print("events.json NOT FOUND")
else:
    print("FOUND FILE:", path)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("Type:", type(data).__name__)

    if isinstance(data, list):
        print("Items:", len(data))
        if len(data) > 0:
            first = data[0]
            print("First item type:", type(first).__name__)
            print("First item:", first)

    elif isinstance(data, dict):
        print("Keys:", list(data.keys()))
        for key, value in data.items():
            print()
            print("Sample key:", key)
            print("Sample value type:", type(value).__name__)
            print("Sample value:", value)
            break

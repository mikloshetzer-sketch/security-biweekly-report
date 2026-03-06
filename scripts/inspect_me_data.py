import os
import json

repo = "me-security-monitor"

print("=== Middle East repo scan ===")
print()

paths_to_check = [
    repo,
    os.path.join(repo, "data"),
    os.path.join(repo, "docs"),
    os.path.join(repo, "docs", "data"),
]

for path in paths_to_check:
    if os.path.exists(path):
        print("Directory:", path)
        try:
            for item in os.listdir(path):
                print(" -", item)
        except Exception as e:
            print("Cannot read directory:", e)
        print()

candidate_files = [
    os.path.join(repo, "events.json"),
    os.path.join(repo, "reports.json"),
    os.path.join(repo, "brief.md"),
    os.path.join(repo, "daily_signal.md"),
    os.path.join(repo, "hotspot_alert.md"),
    os.path.join(repo, "data", "strategic_sites.geojson"),
]

for file_path in candidate_files:
    if os.path.exists(file_path):
        print("FOUND FILE:", file_path)

        if file_path.endswith(".json") or file_path.endswith(".geojson"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                print("Type:", type(data).__name__)

                if isinstance(data, dict):
                    print("Keys:", list(data.keys())[:20])
                elif isinstance(data, list):
                    print("Items:", len(data))
                    if data:
                        print("First item:", data[0])
            except Exception as e:
                print("JSON read error:", e)

        elif file_path.endswith(".md"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                print("Preview:")
                print(content[:1000])
            except Exception as e:
                print("Text read error:", e)

        print()

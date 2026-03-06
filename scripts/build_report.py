import os

print("Biweekly security report generator started")
print()

repos = {
    "Balkan": "balkan-security-map",
    "CEE": "cee-security-map",
    "Middle East": "me-security-monitor"
}

possible_event_files = [
    "data/events.json",
    "docs/data/events.json",
    "events.json"
]

for region, repo in repos.items():
    print(f"Checking {region} repository")

    found = False

    for file in possible_event_files:
        path = os.path.join(repo, file)

        if os.path.exists(path):
            print("EVENT FILE FOUND →", path)
            found = True
            break

    if not found:
        print("No events.json found")

    print()

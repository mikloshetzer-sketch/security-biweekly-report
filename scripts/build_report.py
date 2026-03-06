import os
import json

repos = {
    "Balkan": "balkan-security-map/docs/data/weekly.json",
    "CEE": "cee-security-map/data/weekly.json"
}

print("Checking weekly security data\n")

for region, path in repos.items():

    print("Region:", region)

    if os.path.exists(path):

        with open(path, "r") as f:
            data = json.load(f)

        print("weekly.json found")
        print("records:", len(data))

    else:
        print("weekly.json NOT FOUND")

    print()

import os
import json
from datetime import datetime

sources = {
    "Balkan": "balkan-security-map/docs/data/weekly.json",
    "CEE": "cee-security-map/data/weekly.json"
}

results = {}

print("Checking weekly security data\n")

for region, path in sources.items():

    print("Region:", region)

    if os.path.exists(path):

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        count = len(data)
        results[region] = count

        print("weekly.json found")
        print("records:", count)

    else:

        results[region] = 0
        print("weekly.json NOT FOUND")

    print()


report = f"""
# Biweekly Security Report

Generated: {datetime.utcnow().strftime("%Y-%m-%d")}

## Event overview

Balkan events: {results["Balkan"]}

CEE events: {results["CEE"]}

## Initial assessment

Security events were recorded across the monitored regions.

Further automated analysis will include:
- hotspot detection
- incident categorisation
- trend analysis

Data sources:
- Balkan Security Map
- CEE Security Map
- Middle East Security Monitor
"""


with open("report.md", "w", encoding="utf-8") as f:
    f.write(report)

print("Report generated successfully")

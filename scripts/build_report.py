import os
import json
from datetime import datetime

sources = {
    "Balkan": "balkan-security-map/docs/data/weekly.json",
    "CEE": "cee-security-map/data/weekly.json"
}

results = {}

for region, path in sources.items():

    if os.path.exists(path):

        with open(path, "r") as f:
            data = json.load(f)

        results[region] = len(data)

    else:

        results[region] = 0


report = f"""
# Biweekly Security Report

Generated: {datetime.utcnow().strftime("%Y-%m-%d")}

## Event overview

Balkan events: {results["Balkan"]}

CEE events: {results["CEE"]}

## Initial assessment

Security events were recorded across the monitored regions.

Further automated analysis will include hotspot detection,
incident categorisation and trend analysis.

"""

with open("report.md", "w") as f:
    f.write(report)

print("Report generated successfully")

import os
import json
from datetime import datetime

sources = {
    "Balkans": "balkan-security-map/docs/data/weekly.json",
    "Central and Eastern Europe": "cee-security-map/data/weekly.json"
}

results = {}

for region, path in sources.items():
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        results[region] = len(data)
    else:
        results[region] = 0

total_events = sum(results.values())

report = f"""# Biweekly Security Report

Generated: {datetime.utcnow().strftime("%Y-%m-%d")}

## Executive Summary

A biweekly automated review detected {total_events} tracked security items across the monitored European theatres.
At this stage, the report provides a baseline regional overview based on weekly aggregated monitoring outputs.

## Regional Developments

### Balkans
Recorded events: {results["Balkans"]}

The Balkans monitoring stream remains active and continues to provide weekly incident-level inputs for regional assessment.

### Central and Eastern Europe
Recorded events: {results["Central and Eastern Europe"]}

The Central and Eastern Europe monitoring stream remains active and contributes comparable weekly data for structured review.

### Middle East
Middle East integration is prepared as the next development step and will be connected to the common reporting framework.

## Hotspots

Hotspot extraction will be added in the next development phase using hotspot source files from the regional repositories.

## Security Trend Analysis

Trend analysis will be expanded in the next iteration with hotspot comparison and category-based event interpretation.

## Risk Outlook

The current automated baseline suggests continued relevance of regional monitoring across the Balkans and Central and Eastern Europe.
A more precise short-term risk outlook will be added after hotspot and Middle East integration.

## Methodology

This report is generated automatically from regional monitoring repositories and currently uses weekly aggregated outputs as source inputs.

## Data Sources

- Balkan Security Map
- CEE Security Map
- Middle East Security Monitor
"""

with open("report.md", "w", encoding="utf-8") as f:
    f.write(report)

print("Report generated successfully")

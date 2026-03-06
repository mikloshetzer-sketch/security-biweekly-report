import os
import json
import matplotlib.pyplot as plt

weekly_sources = {
    "Balkans": "balkan-security-map/docs/data/weekly.json",
    "Central & Eastern Europe": "cee-security-map/data/weekly.json"
}

hotspot_sources = {
    "balkan-security-map/docs/data/hotspots.json",
    "cee-security-map/data/hotspots.json"
}

middle_east_events_path = "me-security-monitor/events.json"


def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def sum_counts(data):
    if not isinstance(data, dict):
        return 0
    counts = data.get("counts", {})
    if not isinstance(counts, dict):
        return 0
    return sum(v for v in counts.values() if isinstance(v, (int, float)))


def get_event_counts():

    counts = {}

    for region, path in weekly_sources.items():
        data = load_json(path)
        counts[region] = sum_counts(data)

    me_data = load_json(middle_east_events_path)
    counts["Middle East"] = len(me_data) if isinstance(me_data, list) else 0

    return counts


def create_incident_chart():

    counts = get_event_counts()

    regions = list(counts.keys())
    values = list(counts.values())

    plt.figure()

    plt.bar(regions, values)

    plt.title("Security Incidents by Region")
    plt.ylabel("Number of incidents")

    plt.tight_layout()

    plt.savefig("incident_chart.png")
    plt.close()


def get_hotspots():

    hotspots = []

    paths = [
        "balkan-security-map/docs/data/hotspots.json",
        "cee-security-map/data/hotspots.json"
    ]

    for path in paths:

        data = load_json(path)

        if not isinstance(data, dict):
            continue

        top = data.get("top", [])

        for h in top[:5]:

            lat = h.get("lat")
            lon = h.get("lon")

            if lat is not None and lon is not None:
                hotspots.append((lon, lat))

    return hotspots


def create_hotspot_map():

    hotspots = get_hotspots()

    if not hotspots:
        return

    lons = [p[0] for p in hotspots]
    lats = [p[1] for p in hotspots]

    plt.figure()

    plt.scatter(lons, lats)

    plt.title("Regional Security Hotspots")

    plt.xlabel("Longitude")
    plt.ylabel("Latitude")

    plt.tight_layout()

    plt.savefig("hotspot_map.png")
    plt.close()


def main():

    create_incident_chart()
    create_hotspot_map()

    print("Visuals generated successfully")


if __name__ == "__main__":
    main()

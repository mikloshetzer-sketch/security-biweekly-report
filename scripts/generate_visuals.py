import os
import json
import matplotlib.pyplot as plt


def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_all_hotspots():
    files = [
        "balkan-security-map/docs/data/hotspots.json",
        "cee-security-map/data/hotspots.json"
    ]

    all_hotspots = []

    for path in files:
        data = load_json(path)

        if not isinstance(data, dict):
            continue

        top = data.get("top", [])
        if not isinstance(top, list):
            continue

        for item in top:
            if not isinstance(item, dict):
                continue

            place = item.get("place", "Unknown location")
            change_pct = item.get("change_pct", 0)
            lat = item.get("lat")
            lon = item.get("lon")

            try:
                change_pct = float(change_pct)
            except Exception:
                change_pct = 0.0

            all_hotspots.append({
                "place": place,
                "change_pct": change_pct,
                "lat": lat,
                "lon": lon
            })

    return all_hotspots


def create_growth_chart():
    hotspots = get_all_hotspots()

    hotspots = sorted(
        hotspots,
        key=lambda x: x["change_pct"],
        reverse=True
    )[:6]

    if not hotspots:
        return

    labels = [h["place"] for h in hotspots]
    values = [h["change_pct"] for h in hotspots]

    plt.figure(figsize=(10, 5))
    plt.bar(labels, values)
    plt.title("Top 6 Hotspot Growth Rate (%)")
    plt.ylabel("Growth rate (%)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig("growth_chart.png")
    plt.close()


def create_hotspot_map():
    hotspots = get_all_hotspots()[:10]

    coords = [
        (h["lon"], h["lat"])
        for h in hotspots
        if h["lon"] is not None and h["lat"] is not None
    ]

    if not coords:
        return

    lons = [c[0] for c in coords]
    lats = [c[1] for c in coords]

    plt.figure(figsize=(8, 5))
    plt.scatter(lons, lats)
    plt.title("Regional Hotspot Locations")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.tight_layout()
    plt.savefig("hotspot_map.png")
    plt.close()


def main():
    create_growth_chart()
    create_hotspot_map()
    print("Visuals generated successfully")


if __name__ == "__main__":
    main()

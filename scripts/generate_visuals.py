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

            place = item.get("place", "Unknown")
            lat = item.get("lat")
            lon = item.get("lon")
            change_pct = item.get("change_pct", 0)
            score = item.get("score", 0)

            try:
                change_pct = float(change_pct)
            except Exception:
                change_pct = 0.0

            try:
                score = float(score)
            except Exception:
                score = 0.0

            if lat is None or lon is None:
                continue

            all_hotspots.append({
                "place": place,
                "lat": lat,
                "lon": lon,
                "change_pct": change_pct,
                "score": score
            })

    return all_hotspots


def hotspot_color(change_pct):
    if change_pct >= 300:
        return "red"
    if change_pct >= 100:
        return "orange"
    return "green"


def hotspot_size(score):
    if score >= 25:
        return 70
    if score >= 15:
        return 50
    return 35


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


def draw_geojson_boundaries(path):
    data = load_json(path)

    if not isinstance(data, dict):
        return

    features = data.get("features", [])

    for feature in features:
        geom = feature.get("geometry", {})

        if geom.get("type") == "Polygon":
            for ring in geom.get("coordinates", []):
                xs = [p[0] for p in ring]
                ys = [p[1] for p in ring]
                plt.plot(xs, ys, linewidth=0.5)

        elif geom.get("type") == "MultiPolygon":
            for poly in geom.get("coordinates", []):
                for ring in poly:
                    xs = [p[0] for p in ring]
                    ys = [p[1] for p in ring]
                    plt.plot(xs, ys, linewidth=0.5)


def create_hotspot_map():
    hotspots = get_all_hotspots()[:10]

    if not hotspots:
        return

    plt.figure(figsize=(9, 5.5))

    draw_geojson_boundaries("balkan-security-map/docs/data/balkan_countries.geojson")
    draw_geojson_boundaries("cee-security-map/data/cee_countries.geojson")

    for h in hotspots:
        color = hotspot_color(h["change_pct"])
        size = hotspot_size(h["score"])

        plt.scatter(
            h["lon"],
            h["lat"],
            s=size,
            c=color,
            alpha=0.8
        )

        plt.text(
            h["lon"] + 0.15,
            h["lat"] + 0.10,
            h["place"],
            fontsize=7
        )

    plt.xlim(10, 30)
    plt.ylim(35, 55)

    plt.title("Regional Security Hotspots")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")

    legend_handles = [
        plt.Line2D([0], [0], marker="o", color="w", label="High growth", markerfacecolor="red", markersize=8),
        plt.Line2D([0], [0], marker="o", color="w", label="Medium growth", markerfacecolor="orange", markersize=8),
        plt.Line2D([0], [0], marker="o", color="w", label="Lower / stable", markerfacecolor="green", markersize=8),
    ]
    plt.legend(handles=legend_handles, loc="lower left")

    plt.tight_layout()
    plt.savefig("hotspot_map.png")
    plt.close()


def main():
    create_growth_chart()
    create_hotspot_map()
    print("Visuals generated successfully")


if __name__ == "__main__":
    main()

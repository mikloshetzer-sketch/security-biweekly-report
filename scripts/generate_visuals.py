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

        for item in top:

            place = item.get("place", "Unknown")
            lat = item.get("lat")
            lon = item.get("lon")
            change_pct = item.get("change_pct", 0)

            try:
                change_pct = float(change_pct)
            except:
                change_pct = 0

            if lat is None or lon is None:
                continue

            all_hotspots.append({
                "place": place,
                "lat": lat,
                "lon": lon,
                "change_pct": change_pct
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

    plt.figure(figsize=(10,5))

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

            for ring in geom["coordinates"]:

                xs = [p[0] for p in ring]
                ys = [p[1] for p in ring]

                plt.plot(xs, ys, linewidth=0.5)

        if geom.get("type") == "MultiPolygon":

            for poly in geom["coordinates"]:

                for ring in poly:

                    xs = [p[0] for p in ring]
                    ys = [p[1] for p in ring]

                    plt.plot(xs, ys, linewidth=0.5)


def create_hotspot_map():

    hotspots = get_all_hotspots()[:10]

    if not hotspots:
        return

    plt.figure(figsize=(8,5))

    # Balkán és CEE országhatárok
    draw_geojson_boundaries("balkan-security-map/docs/data/balkan_countries.geojson")
    draw_geojson_boundaries("cee-security-map/data/cee_countries.geojson")

    for h in hotspots:

        plt.scatter(h["lon"], h["lat"], s=30)

        plt.text(
            h["lon"],
            h["lat"],
            h["place"],
            fontsize=7
        )

    plt.xlim(10, 30)
    plt.ylim(35, 55)

    plt.title("Regional Security Hotspots")

    plt.tight_layout()

    plt.savefig("hotspot_map.png")

    plt.close()


def main():

    create_growth_chart()

    create_hotspot_map()

    print("Visuals generated successfully")


if __name__ == "__main__":
    main()

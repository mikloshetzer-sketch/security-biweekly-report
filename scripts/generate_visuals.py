import os
import json
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


BASE_MAP_PATH = "assets/Európa.jpg"


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
        return 90
    if score >= 15:
        return 65
    return 45


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

    if not hotspots:
        return

    if not os.path.exists(BASE_MAP_PATH):
        print(f"Base map not found: {BASE_MAP_PATH}")
        return

    img = mpimg.imread(BASE_MAP_PATH)

    plt.figure(figsize=(10, 6))
    plt.imshow(
        img,
        extent=[-30, 150, 0, 80],
        aspect="auto"
    )

    for h in hotspots:
        color = hotspot_color(h["change_pct"])
        size = hotspot_size(h["score"])

        plt.scatter(
            h["lon"],
            h["lat"],
            s=size,
            c=color,
            alpha=0.85,
            edgecolors="black",
            linewidths=0.5
        )

        plt.text(
            h["lon"] + 0.8,
            h["lat"] + 0.5,
            h["place"],
            fontsize=7,
            color="black"
        )

    plt.xlim(-30, 150)
    plt.ylim(0, 80)

    plt.title("Regional Security Hotspots")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")

    legend_handles = [
        plt.Line2D(
            [0], [0],
            marker="o",
            color="w",
            label="High growth",
            markerfacecolor="red",
            markeredgecolor="black",
            markersize=8
        ),
        plt.Line2D(
            [0], [0],
            marker="o",
            color="w",
            label="Medium growth",
            markerfacecolor="orange",
            markeredgecolor="black",
            markersize=8
        ),
        plt.Line2D(
            [0], [0],
            marker="o",
            color="w",
            label="Lower / stable",
            markerfacecolor="green",
            markeredgecolor="black",
            markersize=8
        ),
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

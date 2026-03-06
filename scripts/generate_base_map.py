import os
import json
import matplotlib.pyplot as plt


def load_json(path):
    if not os.path.exists(path):
        return None

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def draw_geojson_boundaries(ax, path):

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

                ax.plot(xs, ys, linewidth=0.6, color="black")

        elif geom.get("type") == "MultiPolygon":

            for poly in geom["coordinates"]:

                for ring in poly:

                    xs = [p[0] for p in ring]
                    ys = [p[1] for p in ring]

                    ax.plot(xs, ys, linewidth=0.6, color="black")


def generate_map():

    # csak akkor hozza létre ha nincs
    if not os.path.isdir("assets"):
        os.mkdir("assets")

    fig, ax = plt.subplots(figsize=(12,8))

    ax.set_facecolor("white")

    draw_geojson_boundaries(
        ax,
        "balkan-security-map/docs/data/balkan_countries.geojson"
    )

    draw_geojson_boundaries(
        ax,
        "cee-security-map/data/cee_countries.geojson"
    )

    ax.set_xlim(-10, 45)
    ax.set_ylim(30, 72)

    ax.set_xticks([])
    ax.set_yticks([])

    ax.set_title("Europe Base Map", fontsize=14)

    plt.tight_layout()

    plt.savefig(
        "assets/europe_base_map.png",
        dpi=300
    )

    plt.close()


if __name__ == "__main__":

    generate_map()

    print("Base map generated successfully")

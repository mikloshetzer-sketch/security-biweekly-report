import os

print("Scanning repositories for data files")
print()

repos = {
    "Balkan": "balkan-security-map",
    "CEE": "cee-security-map",
    "Middle East": "me-security-monitor"
}

for region, repo in repos.items():

    print("----", region, "----")

    paths = [
        repo + "/data",
        repo + "/docs/data"
    ]

    for p in paths:
        if os.path.exists(p):

            print("Directory:", p)

            files = os.listdir(p)

            for f in files:
                print(" -", f)

    print()

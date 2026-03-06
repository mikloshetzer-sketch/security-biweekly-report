import os

print("Biweekly security report generator started")
print()

repos = [
    "balkan-security-map",
    "cee-security-map",
    "me-security-monitor"
]

print("Checking cloned repositories:")
print()

for repo in repos:
    if os.path.exists(repo):
        print(f"{repo} → FOUND")
        print("Files inside:")
        try:
            files = os.listdir(repo)
            for f in files[:10]:
                print(" -", f)
        except:
            print("Cannot read files")
        print()
    else:
        print(f"{repo} → NOT FOUND")

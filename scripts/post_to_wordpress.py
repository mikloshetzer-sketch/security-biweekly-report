import os
from pathlib import Path
from datetime import datetime, UTC

import requests

REPORT_FILE = Path("report.md")

TOKEN = os.environ["WPCOM_ACCESS_TOKEN"]
SITE = os.environ["WPCOM_SITE"]

title = f"Security Biweekly Report - {datetime.now(UTC).strftime('%Y-%m-%d')}"

if not REPORT_FILE.exists():
    raise SystemExit("Nincs report.md fájl.")

content = REPORT_FILE.read_text(encoding="utf-8").strip()

if not content:
    raise SystemExit("A report.md üres.")

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

# 1. Megnézzük, van-e már ilyen című poszt
search_url = f"https://public-api.wordpress.com/rest/v1.1/sites/{SITE}/posts"
search_response = requests.get(
    search_url,
    headers=headers,
    params={"search": title},
    timeout=60,
)

print("SEARCH STATUS:", search_response.status_code)
print("SEARCH RESPONSE:", search_response.text)

search_response.raise_for_status()
search_data = search_response.json()

if search_data.get("found", 0) > 0:
    raise SystemExit("Már létezik ilyen című poszt, kihagyva.")

# 2. Új poszt létrehozása
post_url = f"https://public-api.wordpress.com/rest/v1.1/sites/{SITE}/posts/new"
post_response = requests.post(
    post_url,
    headers=headers,
    data={
        "title": title,
        "content": content,
        "status": "publish",
    },
    timeout=60,
)

print("POST STATUS:", post_response.status_code)
print("POST RESPONSE:", post_response.text)

post_response.raise_for_status()

import os
import requests
from pathlib import Path
from datetime import datetime

REPORT_FILE = Path("report.md")

TOKEN = os.environ["WPCOM_ACCESS_TOKEN"]
SITE = os.environ["WPCOM_SITE"]

title = "Security Biweekly Report – " + datetime.utcnow().strftime("%Y-%m-%d")

content = REPORT_FILE.read_text()

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

# 1. Ellenőrizzük van-e már ilyen című poszt
search_url = f"https://public-api.wordpress.com/rest/v1.1/sites/{SITE}/posts/?search={title}"
search = requests.get(search_url, headers=headers).json()

if search.get("found", 0) > 0:
    print("Post already exists. Skipping.")
    exit()

# 2. Új poszt létrehozása
url = f"https://public-api.wordpress.com/rest/v1.1/sites/{SITE}/posts/new"

response = requests.post(
    url,
    headers=headers,
    data={
        "title": title,
        "content": content,
        "status": "publish"
    }
)

print(response.text)

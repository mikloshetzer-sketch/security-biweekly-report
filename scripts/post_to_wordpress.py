import os
import requests
from pathlib import Path

REPORT_FILE = Path("report.md")

TOKEN = os.environ["WPCOM_ACCESS_TOKEN"]
SITE = os.environ["WPCOM_SITE"]

url = f"https://public-api.wordpress.com/rest/v1.1/sites/{SITE}/posts/new"

content = REPORT_FILE.read_text()

response = requests.post(
    url,
    headers={
        "Authorization": f"Bearer {TOKEN}"
    },
    data={
        "title": "Security Biweekly Report",
        "content": content,
        "status": "draft"
    }
)

print(response.text)

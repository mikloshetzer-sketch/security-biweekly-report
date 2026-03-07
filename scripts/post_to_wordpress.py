import os
from pathlib import Path
from datetime import datetime, timezone

import requests
import markdown

REPORT_FILE = Path("report.md")

TOKEN = os.environ["WPCOM_ACCESS_TOKEN"]
SITE = os.environ["WPCOM_SITE"]

if not REPORT_FILE.exists():
    raise SystemExit("report.md not found")

md_text = REPORT_FILE.read_text(encoding="utf-8").strip()

if not md_text:
    raise SystemExit("report.md is empty")

title = "Security Biweekly Report - " + datetime.now(timezone.utc).strftime("%Y-%m-%d")

html_body = markdown.markdown(
    md_text,
    extensions=["extra", "tables", "fenced_code", "nl2br"]
)

styled_content = f"""
<div style="background:#4b5563;padding:40px 20px;">
  <div style="max-width:1000px;margin:0 auto;display:flex;flex-direction:column;gap:30px;">

    <div style="background:#f8fafc;color:#1f2937;padding:36px;border-radius:18px;box-shadow:0 10px 25px rgba(0,0,0,0.2);line-height:1.75;font-size:18px;">
      {html_body}
    </div>

  </div>
</div>
"""

url = f"https://public-api.wordpress.com/rest/v1.1/sites/{SITE}/posts/new"

response = requests.post(
    url,
    headers={
        "Authorization": f"Bearer {TOKEN}"
    },
    data={
        "title": title,
        "content": styled_content,
        "status": "publish"
    },
    timeout=60
)

print("STATUS:", response.status_code)
print("RESPONSE:", response.text)

response.raise_for_status()

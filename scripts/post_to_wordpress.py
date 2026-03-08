import os
import re
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


def split_sections(md):
    parts = re.split(r"\n## ", md)
    sections = []

    for i, part in enumerate(parts):
        if i == 0:
            sections.append(part)
        else:
            sections.append("## " + part)

    return sections


def render(md):
    return markdown.markdown(md, extensions=["extra", "tables", "fenced_code", "nl2br"])


def style_html(html):

    html = re.sub(
        r"<h1>(.*?)</h1>",
        r'<h1 style="font-size:28px;margin-bottom:16px;color:#0f172a;">\1</h1>',
        html,
    )

    html = re.sub(
        r"<h2>(.*?)</h2>",
        r'<h2 style="font-size:20px;margin-bottom:14px;color:#0f172a;">\1</h2>',
        html,
    )

    html = re.sub(
        r"<h3>(.*?)</h3>",
        r'<h3 style="font-size:18px;margin-top:18px;margin-bottom:10px;color:#1e293b;">\1</h3>',
        html,
    )

    html = re.sub(
        r"<p>(.*?)</p>",
        r'<p style="font-size:16px;line-height:1.7;margin-bottom:14px;color:#334155;">\1</p>',
        html,
    )

    return html


sections = split_sections(md_text)

cards = []

for sec in sections:

    html = style_html(render(sec))

    cards.append(f"""
    <div style="
        background:#f8fafc;
        padding:28px;
        border-radius:18px;
        box-shadow:0 8px 20px rgba(0,0,0,0.15);
    ">
        {html}
    </div>
    """)

styled_content = f"""
<div style="background:#4b5563;padding:40px 20px;">
  <div style="max-width:1000px;margin:0 auto;display:flex;flex-direction:column;gap:26px;">

    <div style="
        background:linear-gradient(135deg,#475569,#334155);
        padding:28px;
        border-radius:22px;
        color:#f1f5f9;
        box-shadow:0 12px 30px rgba(0,0,0,0.25);
    ">
        <div style="font-size:13px;text-transform:uppercase;letter-spacing:1px;">
        Security Biweekly Monitor
        </div>

        <div style="font-size:30px;font-weight:700;margin-top:6px;">
        {title}
        </div>

    </div>

    {''.join(cards)}

  </div>
</div>
"""

url = f"https://public-api.wordpress.com/rest/v1.1/sites/{SITE}/posts/new"

response = requests.post(
    url,
    headers={"Authorization": f"Bearer {TOKEN}"},
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

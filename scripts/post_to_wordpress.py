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


def split_into_sections(md: str):
    lines = md.splitlines()
    sections = []
    current_title = None
    current_lines = []

    for line in lines:
        if line.startswith("## "):
            if current_title is not None or current_lines:
                sections.append((current_title, "\n".join(current_lines).strip()))
            current_title = line[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_title is not None or current_lines:
        sections.append((current_title, "\n".join(current_lines).strip()))

    return sections


def render_markdown(md: str) -> str:
    return markdown.markdown(
        md,
        extensions=["extra", "tables", "fenced_code", "nl2br"]
    )


def style_html(html: str) -> str:
    html = re.sub(
        r"<h1>(.*?)</h1>",
        r'<h1 style="font-size:34px;line-height:1.2;margin:0 0 18px 0;color:#0f172a;">\1</h1>',
        html,
        flags=re.DOTALL,
    )
    html = re.sub(
        r"<h2>(.*?)</h2>",
        r'<h2 style="font-size:24px;line-height:1.3;margin:0 0 18px 0;color:#0f172a;">\1</h2>',
        html,
        flags=re.DOTALL,
    )
    html = re.sub(
        r"<h3>(.*?)</h3>",
        r'<h3 style="font-size:20px;line-height:1.35;margin:24px 0 12px 0;color:#1e293b;">\1</h3>',
        html,
        flags=re.DOTALL,
    )
    html = re.sub(
        r"<p>(.*?)</p>",
        r'<p style="margin:0 0 16px 0;font-size:17px;line-height:1.8;color:#334155;">\1</p>',
        html,
        flags=re.DOTALL,
    )
    html = re.sub(
        r"<ul>",
        r'<ul style="margin:0 0 18px 20px;padding:0;color:#334155;line-height:1.8;">',
        html,
        flags=re.DOTALL,
    )
    html = re.sub(
        r"<ol>",
        r'<ol style="margin:0 0 18px 20px;padding:0;color:#334155;line-height:1.8;">',
        html,
        flags=re.DOTALL,
    )
    html = re.sub(
        r"<li>(.*?)</li>",
        r'<li style="margin:0 0 10px 0;">\1</li>',
        html,
        flags=re.DOTALL,
    )
    html = re.sub(
        r"<blockquote>(.*?)</blockquote>",
        r'<blockquote style="margin:24px 0;padding:16px 20px;border-left:4px solid #64748b;background:#f1f5f9;color:#334155;border-radius:10px;">\1</blockquote>',
        html,
        flags=re.DOTALL,
    )
    html = re.sub(
        r"<table>",
        r'<table style="width:100%;border-collapse:collapse;margin:24px 0;background:#ffffff;border-radius:12px;overflow:hidden;">',
        html,
        flags=re.DOTALL,
    )
    html = re.sub(
        r"<th>(.*?)</th>",
        r'<th style="text-align:left;padding:12px 14px;background:#e2e8f0;color:#0f172a;border:1px solid #cbd5e1;">\1</th>',
        html,
        flags=re.DOTALL,
    )
    html = re.sub(
        r"<td>(.*?)</td>",
        r'<td style="padding:12px 14px;border:1px solid #cbd5e1;color:#334155;">\1</td>',
        html,
        flags=re.DOTALL,
    )
    html = re.sub(
        r"<code>(.*?)</code>",
        r'<code style="background:#e2e8f0;color:#0f172a;padding:2px 6px;border-radius:6px;font-size:14px;">\1</code>',
        html,
        flags=re.DOTALL,
    )
    html = re.sub(
        r"<pre>(.*?)</pre>",
        r'<pre style="background:#0f172a;color:#e2e8f0;padding:18px;border-radius:12px;overflow-x:auto;margin:24px 0;"><code>\1</code></pre>',
        html,
        flags=re.DOTALL,
    )
    return html


sections = split_into_sections(md_text)

intro_html = ""
section_cards = []

for index, (section_title, section_md) in enumerate(sections):
    combined_md = ""
    if section_title:
        combined_md += f"## {section_title}\n\n"
    if section_md:
        combined_md += section_md

    rendered = style_html(render_markdown(combined_md))

    if index == 0 and not section_title:
        intro_html = f"""
        <div style="background:#f8fafc;color:#1f2937;padding:36px;border-radius:20px;box-shadow:0 10px 25px rgba(0,0,0,0.18);">
          {rendered}
        </div>
        """
    else:
        section_cards.append(f"""
        <div style="background:#f8fafc;color:#1f2937;padding:32px;border-radius:20px;box-shadow:0 10px 25px rgba(0,0,0,0.16);border-top:6px solid #94a3b8;">
          {rendered}
        </div>
        """)

if not intro_html:
    intro_html = f"""
    <div style="background:#f8fafc;color:#1f2937;padding:36px;border-radius:20px;box-shadow:0 10px 25px rgba(0,0,0,0.18);">
      <h1 style="font-size:34px;line-height:1.2;margin:0;color:#0f172a;">{title}</h1>
    </div>
    """

styled_content = f"""
<div style="background:#4b5563;padding:40px 20px;">
  <div style="max-width:1000px;margin:0 auto;display:flex;flex-direction:column;gap:28px;">

    <div style="background:linear-gradient(135deg,#475569 0%,#334155 100%);padding:34px;border-radius:24px;box-shadow:0 12px 30px rgba(0,0,0,0.22);">
      <div style="font-size:13px;letter-spacing:1.5px;text-transform:uppercase;color:#cbd5e1;margin-bottom:10px;">
        Security Biweekly Monitor
      </div>
      <div style="font-size:36px;font-weight:700;line-height:1.2;color:#f8fafc;">
        {title}
      </div>
      <div style="margin-top:10px;font-size:16px;color:#e2e8f0;">
        Automated report published from GitHub to WordPress
      </div>
    </div>

    {intro_html}

    {''.join(section_cards)}

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

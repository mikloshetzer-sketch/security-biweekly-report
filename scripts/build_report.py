import os
import json
from datetime import datetime


weekly_sources = {
    "Balkán": "balkan-security-map/docs/data/weekly.json",
    "Közép- és Kelet-Európa": "cee-security-map/data/weekly.json"
}

hotspot_sources = {
    "Balkán": "balkan-security-map/docs/data/hotspots.json",
    "Közép- és Kelet-Európa": "cee-security-map/data/hotspots.json"
}

middle_east_events_path = "me-security-monitor/events.json"


def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def safe_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


def safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


def format_change_pct(value):
    try:
        return f"{float(value):.1f}%"
    except Exception:
        return "n.a."


def get_event_counts():
    results = {}
    for region, path in weekly_sources.items():
        data = load_json(path)
        if isinstance(data, list):
            results[region] = len(data)
        else:
            results[region] = 0
    return results


def get_top_hotspots(path, limit=3):
    data = load_json(path)
    if not isinstance(data, dict):
        return []

    hotspots = data.get("top", [])
    if not isinstance(hotspots, list):
        return []

    return hotspots[:limit]


def detect_signal_type(sources):
    if not isinstance(sources, dict):
        return (
            "nem meghatározható jelzéstípus",
            "unclassified signal"
        )

    gdelt = sources.get("GDELT", 0)
    usgs = sources.get("USGS", 0)
    gdacs = sources.get("GDACS", 0)

    active = []
    if gdelt > 0:
        active.append("GDELT")
    if usgs > 0:
        active.append("USGS")
    if gdacs > 0:
        active.append("GDACS")

    if active == ["GDELT"]:
        return (
            "hír- és médiamonitoring alapú incidensjelzés",
            "news and media monitoring-based signal"
        )
    if active == ["USGS"]:
        return (
            "szeizmikus eseményjelzés",
            "seismic activity signal"
        )
    if active == ["GDACS"]:
        return (
            "katasztrófa-riasztási jelzés",
            "disaster alert signal"
        )
    if "GDELT" in active and ("USGS" in active or "GDACS" in active):
        return (
            "összetett, több forrásból származó jelzés",
            "multi-source composite signal"
        )
    if "USGS" in active and "GDACS" in active:
        return (
            "természeti veszélyhelyzeti jelzés",
            "natural hazard signal"
        )

    return (
        "vegyes vagy korlátozottan azonosítható jelzés",
        "mixed or weakly identifiable signal"
    )


def hotspot_type_label(sources):
    if not isinstance(sources, dict):
        return "Vegyes / Mixed"

    gdelt = sources.get("GDELT", 0)
    usgs = sources.get("USGS", 0)
    gdacs = sources.get("GDACS", 0)

    if gdelt > 0 and usgs == 0 and gdacs == 0:
        return "Politikai / biztonsági incidensjelzés"
    if usgs > 0 and gdelt == 0 and gdacs == 0:
        return "Szeizmikus aktivitás"
    if gdacs > 0 and gdelt == 0 and usgs == 0:
        return "Katasztrófa-riasztás"
    if gdelt > 0 and (usgs > 0 or gdacs > 0):
        return "Összetett biztonsági jelzés"
    if usgs > 0 and gdacs > 0:
        return "Természeti veszélyhelyzet"

    return "Vegyes / Mixed"


def hotspot_analysis_paragraphs(hotspot):
    place = hotspot.get("place", "Ismeretlen helyszín")
    count = safe_int(hotspot.get("count", 0))
    trend = hotspot.get("trend", "stable")
    change_pct = format_change_pct(hotspot.get("change_pct", 0))
    score = safe_float(hotspot.get("score", 0))
    sources = hotspot.get("sources", {})

    signal_type_hu, signal_type_en = detect_signal_type(sources)
    label = hotspot_type_label(sources)

    if trend == "up":
        trend_hu = "növekvő incidensaktivitás figyelhető meg"
        trend_en = "an upward trend in incident activity can be observed"
    elif trend == "down":
        trend_hu = "az aktivitás mérséklődése figyelhető meg"
        trend_en = "a declining trend in activity can be observed"
    else:
        trend_hu = "az aktivitás viszonylag stabil képet mutat"
        trend_en = "activity appears relatively stable"

    if count >= 60:
        density_hu = "kiemelkedően magas eseménysűrűséget"
        density_en = "a particularly high event density"
    elif count >= 40:
        density_hu = "jelentős eseménysűrűséget"
        density_en = "a significant event density"
    elif count >= 20:
        density_hu = "érzékelhető eseménysűrűséget"
        density_en = "a noticeable event density"
    else:
        density_hu = "korlátozott, de releváns aktivitást"
        density_en = "limited but relevant activity"

    paragraph_hu = (
        f"**{place}**  \n"
        f"Az elmúlt időszak fejleményei arra utalnak, hogy {place} térségében {trend_hu}. "
        f"A monitoring rendszer {density_hu} azonosított, az aktivitásváltozás mértéke pedig {change_pct}. "
        f"A jelenlegi jelzések elsődlegesen {signal_type_hu} formájában jelentkeznek.  \n"
        f"Jelzés típusa: **{label}**. "
        f"A jelenlegi trendek alapján valószínűsíthető, hogy a térség rövid távon is a regionális figyelem egyik fontos pontja marad. "
        f"A hotspot intenzitási pontszáma: **{score:.3f}**."
    )

    paragraph_en = (
        f"**{place}**  \n"
        f"Recent developments suggest that {trend_en} in the {place} area. "
        f"The monitoring system detected {density_en}, while the change in activity reached {change_pct}. "
        f"Current signals are primarily identified as {signal_type_en}.  \n"
        f"Signal type: **{label}**. "
        f"Current trends suggest that this location is likely to remain an important focal point of regional monitoring in the short term. "
        f"Hotspot intensity score: **{score:.3f}**."
    )

    return paragraph_hu, paragraph_en


def build_hotspot_section():
    sections = []

    for region, path in hotspot_sources.items():
        hotspots = get_top_hotspots(path, limit=3)

        sections.append(f"### {region}")

        if not hotspots:
            sections.append("Nem áll rendelkezésre értékelhető hotspot adat.\n")
            continue

        for hotspot in hotspots:
            hu, en = hotspot_analysis_paragraphs(hotspot)
            sections.append(hu)
            sections.append("")
            sections.append(en)
            sections.append("")
        sections.append("")

    return "\n".join(sections)


def get_middle_east_events(limit=3):
    data = load_json(middle_east_events_path)
    if not isinstance(data, list):
        return [], 0

    total = len(data)

    # Egyszerű prioritás: magasabb confidence, utána frissebb rekordok maradjanak elöl
    sorted_events = sorted(
        data,
        key=lambda x: (
            safe_float(x.get("confidence", 0), 0.0),
            x.get("date", "")
        ),
        reverse=True
    )

    return sorted_events[:limit], total


def classify_me_signal(event):
    source = event.get("source", {}) if isinstance(event, dict) else {}
    source_type = source.get("type", "")
    category = event.get("category", "other")

    if source_type == "news":
        if category in ["conflict", "security", "politics"]:
            return (
                "hír alapú biztonsági-politikai jelzés",
                "news-based political-security signal"
            )
        if category in ["economy", "energy"]:
            return (
                "hír alapú gazdasági vagy energiapiaci jelzés",
                "news-based economic or energy-market signal"
            )
        return (
            "hír alapú regionális incidensjelzés",
            "news-based regional incident signal"
        )

    return (
        "általános monitoring jelzés",
        "general monitoring signal"
    )


def middle_east_event_paragraphs(event):
    title = event.get("title", "Untitled event")
    summary = event.get("summary", "")
    category = event.get("category", "other")
    confidence = safe_float(event.get("confidence", 0), 0.0)
    date = event.get("date", "n.a.")

    source = event.get("source", {}) if isinstance(event.get("source", {}), dict) else {}
    source_name = source.get("name", "Unknown source")

    location = event.get("location", {}) if isinstance(event.get("location", {}), dict) else {}
    location_name = location.get("name", "Middle East")

    signal_hu, signal_en = classify_me_signal(event)

    category_map_hu = {
        "other": "egyéb regionális fejlemény",
        "security": "biztonsági fejlemény",
        "politics": "politikai fejlemény",
        "conflict": "konfliktushoz kapcsolódó fejlemény",
        "economy": "gazdasági fejlemény",
        "energy": "energiapiaci fejlemény"
    }

    category_hu = category_map_hu.get(category, "regionális fejlemény")

    paragraph_hu = (
        f"**{title}**  \n"
        f"Dátum: **{date}** | Helyszín: **{location_name}** | Forrás: **{source_name}**  \n"
        f"Az esemény {signal_hu} kategóriába sorolható, és a monitoring rendszer {confidence:.2f} bizalmi szint mellett kezelte. "
        f"A rendelkezésre álló összefoglaló alapján ez egy **{category_hu}**, amely hozzájárul a térség folyamatos stratégiai bizonytalanságához. "
        f"{summary}"
    )

    paragraph_en = (
        f"**{title}**  \n"
        f"Date: **{date}** | Location: **{location_name}** | Source: **{source_name}**  \n"
        f"This event can be classified as a {signal_en}, and it was handled by the monitoring system with a confidence level of {confidence:.2f}. "
        f"Based on the available summary, this is a **{category}** development contributing to the region's continued strategic uncertainty. "
        f"{summary}"
    )

    return paragraph_hu, paragraph_en


def build_middle_east_section():
    top_events, total = get_middle_east_events(limit=3)

    lines = []
    lines.append("### Közel-Kelet / Middle East")
    lines.append("")
    lines.append(
        f"A monitoring rendszer az aktuális időszakban **{total} közel-keleti eseményt** azonosított. "
        f"Az események túlnyomó része hírforrásokon alapuló regionális jelzésként értelmezhető."
    )
    lines.append("")
    lines.append(
        f"The monitoring system identified **{total} Middle East-related events** in the current dataset. "
        f"Most items can be interpreted as news-based regional signals."
    )
    lines.append("")

    if not top_events:
        lines.append("Nem áll rendelkezésre értékelhető közel-keleti eseményadat.")
        lines.append("")
        lines.append("No evaluable Middle East event data is currently available.")
        lines.append("")
        return "\n".join(lines), total

    lines.append("#### Kiemelt események / Highlighted events")
    lines.append("")

    for event in top_events:
        hu, en = middle_east_event_paragraphs(event)
        lines.append(hu)
        lines.append("")
        lines.append(en)
        lines.append("")

    return "\n".join(lines), total


event_results = get_event_counts()
hotspot_section = build_hotspot_section()
middle_east_section, middle_east_total = build_middle_east_section()

total_events = (
    event_results.get("Balkán", 0)
    + event_results.get("Közép- és Kelet-Európa", 0)
    + middle_east_total
)

date_hu = datetime.utcnow().strftime("%Y-%m-%d")
date_en = datetime.utcnow().strftime("%Y-%m-%d")

report = f"""# REGIONÁLIS BIZTONSÁGPOLITIKAI HELYZETJELENTÉS
# REGIONAL SECURITY SITUATION REPORT

Balkán – Közép- és Kelet-Európa – Közel-Kelet  
Balkans – Central and Eastern Europe – Middle East  

Készítés dátuma: {date_hu}  
Date of issue: {date_en}  

Terjesztés: Nyilvános elemzés  
Distribution: Public analysis  

Készítette: toresvonalak.blog  
Prepared by: toresvonalak.blog  

---

# 1. Vezetői összefoglaló  
## Executive Summary

Az elmúlt időszak fejleményei arra utalnak, hogy a megfigyelt régiókban továbbra is fennmaradnak a biztonsági kockázatok, különösen a regionális politikai feszültségek, a határmenti incidensek és a Közel-Kelethez kapcsolódó stratégiai bizonytalanság tekintetében.

A monitoring rendszer az aktuális időszakban **{total_events} biztonsági relevanciájú eseményt** azonosított a vizsgált térségekben.

A jelenlegi trendek alapján valószínűsíthető, hogy a Balkán és a közép- és kelet-európai térségben alacsony intenzitású, de tartós biztonsági incidensek maradnak jelen, míg a Közel-Kelet továbbra is jelentős politikai, gazdasági és stratégiai kockázati forrásként értékelhető.

Bár közvetlen, nagyszabású katonai konfliktus nem minden térségben várható, a helyzet továbbra is fokozott figyelmet igényel a regionális biztonságpolitikai döntéshozók részéről.

Recent developments indicate that security risks remain present across the monitored regions, particularly with regard to political tensions, localized incident activity and persistent strategic uncertainty linked to the Middle East.

The monitoring system identified **{total_events} security-relevant items** across the currently integrated regional streams.

Current trends suggest that low-intensity but persistent security incidents are likely to remain present in the Balkans and in Central and Eastern Europe, while the Middle East continues to represent a significant source of political, economic and strategic risk.

While direct large-scale military confrontation is not assessed as imminent across all theatres, the overall environment still requires heightened analytical attention.

---

# 2. Aktuális biztonsági helyzet  
## Current Security Situation

### Politikai környezet / Political Environment

A térség politikai rendszerei jelenleg relatív stabilitást mutatnak, ugyanakkor több országban megfigyelhető a politikai polarizáció erősödése és a társadalmi mobilizáció növekedése.

The political systems of the monitored regions currently show relative institutional stability, although political polarization and social mobilization are visible in several countries.

### Katonai és biztonsági helyzet / Military and Security Situation

Balkán régióban azonosított események száma: **{event_results.get("Balkán", 0)}**  
Közép- és Kelet-Európában azonosított események száma: **{event_results.get("Közép- és Kelet-Európa", 0)}**  
Közel-Kelethez kapcsolódó azonosított események száma: **{middle_east_total}**

Az incidensek többsége alacsony intenzitású eseményekhez, politikai feszültségekhez vagy biztonsági incidensekhez kapcsolódik, miközben a közel-keleti adatfolyam jelentős részben hír alapú regionális fejleményeket követ.

Most detected items remain linked to low-intensity security developments, political tensions or localized incident clusters, while the Middle East data stream is largely driven by news-based regional developments.

{middle_east_section}

---

# 3. Geopolitikai környezet  
## Geopolitical Environment

A térség geopolitikai jelentősége elsősorban abból fakad, hogy több stratégiai jelentőségű energia-, kereskedelmi és politikai útvonal metszéspontjában helyezkedik el.

A jelenlegi geopolitikai dinamikát a nagyhatalmi versengés, a regionális biztonsági architektúra változásai és a gazdasági stabilitás kérdései alakítják.

The geopolitical relevance of the broader area stems primarily from its location along strategic energy, trade and political corridors.

Current regional dynamics are shaped by great-power competition, changing security architectures and questions of economic resilience.

---

# 4. Fő biztonsági kihívások  
## Main Security Challenges

A legjelentősebb kockázatot jelenleg az jelenti, hogy több térségben egyszerre jelentkeznek politikai, gazdasági és biztonsági természetű kihívások.

A térségben az utóbbi időszakban erősödtek a hibrid hadviselés elemei, különösen az információs műveletek és a kibertérhez kapcsolódó sérülékenységek területén.

The most significant current risk lies in the simultaneous presence of political, economic and security pressures across multiple monitored areas.

Hybrid elements have also become more visible, especially in the field of information influence and cyber-related vulnerabilities.

---

# 5. Regionális hotspotok  
## Regional Hotspots

{hotspot_section}

---

# 6. Kockázatelemzés  
## Risk Assessment

| Fenyegetés | Valószínűség | Hatás | Kockázati szint |
|---|---|---|---|
| Határincidensek | magas | közepes | magas |
| Politikai instabilitás | közepes | magas | magas |
| Hibrid műveletek | magas | közepes | magas |
| Nagyhatalmi versengés | közepes | magas | magas |
| Energiapiaci zavarok | közepes | magas | magas |

---

# 7. Előrejelzés  
## Forecast

A jelenlegi trendek alapján valószínűsíthető, hogy a régiókban rövid távon fennmarad az alacsony intenzitású biztonsági feszültség, miközben a Közel-Kelethez kapcsolódó fejlemények továbbra is közvetett hatást gyakorolhatnak a tágabb regionális biztonsági környezetre.

A geopolitikai rivalizálás erősödése következtében a térség továbbra is stratégiai jelentőségű biztonsági térként jelenik meg.

Current trends suggest that low-intensity regional security pressure is likely to persist in the short term, while developments linked to the Middle East may continue to shape the broader regional environment indirectly.

As geopolitical rivalry intensifies, the monitored space will likely continue to function as a strategically relevant security environment.

---

# 8. Ajánlások  
## Recommendations

A regionális stabilitás fenntartása érdekében a következő lépések javasoltak:

- a határ menti katonai kommunikáció erősítése  
- a bizalomépítő intézkedések kiterjesztése  
- a dezinformáció elleni együttműködés növelése  
- a gazdasági stabilitást támogató nemzetközi programok bővítése  
- az energiabiztonsági kitettségek folyamatos monitorozása  

To support regional stability, the following steps are recommended:

- strengthen cross-border military communication  
- expand confidence-building measures  
- increase cooperation against disinformation  
- broaden international programs supporting economic resilience  
- continuously monitor energy-security vulnerabilities  

---

# 9. Módszertan és adatforrások  
## Methodology and Data Sources

A jelentés automatizált monitoring rendszerekből származó adatok feldolgozásán alapul. A jelenlegi verzió a heti összesítések, hotspot-jelzések és a Közel-Kelethez kapcsolódó eseménylisták alapján készül.

This report is based on automated monitoring outputs. The current version relies on weekly aggregation files, hotspot signal summaries and Middle East event lists.

Adatforrások / Data sources:

- Balkan Security Map  
- CEE Security Map  
- Middle East Security Monitor
"""

with open("report.md", "w", encoding="utf-8") as f:
    f.write(report)

print("Security report generated successfully")

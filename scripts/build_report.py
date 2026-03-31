import os
import json
from datetime import datetime


weekly_sources = {
    "Balkán": [
        "balkan-security-map/docs/data/weekly.json",
        "balkan-security-map/data/weekly.json",
    ],
    "Közép- és Kelet-Európa": [
        "cee-security-map/data/weekly.json",
        "cee-security-map/docs/data/weekly.json",
    ]
}

hotspot_sources = {
    "Balkán": [
        "balkan-security-map/docs/data/hotspots.json",
        "balkan-security-map/data/hotspots.json",
    ],
    "Közép- és Kelet-Európa": [
        "cee-security-map/data/hotspots.json",
        "cee-security-map/docs/data/hotspots.json",
    ]
}

middle_east_events_paths = [
    "me-security-monitor/events.json",
    "me-security-monitor/data/events.json",
]


def first_existing_path(paths):
    if isinstance(paths, str):
        return paths if os.path.exists(paths) else None
    for path in paths:
        if os.path.exists(path):
            return path
    return None


def load_json(path_or_paths):
    path = first_existing_path(path_or_paths)
    if not path:
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def safe_int(value, default=0):
    try:
        if value is None:
            return default
        return int(value)
    except Exception:
        return default


def safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def clean_text(value):
    if not isinstance(value, str):
        return ""
    return " ".join(value.replace("\n", " ").split()).strip()


def clip_text(value, max_len=500):
    text = clean_text(value)
    if not text:
        return ""
    if len(text) <= max_len:
        return text
    clipped = text[:max_len].rsplit(" ", 1)[0].strip()
    return clipped + "…"


def ensure_list(value):
    return value if isinstance(value, list) else []


def sum_numeric_values(obj):
    if not isinstance(obj, dict):
        return 0
    total = 0
    for value in obj.values():
        if isinstance(value, (int, float)):
            total += int(value)
    return total


def format_change_pct(value):
    try:
        if value is None:
            return "n.a."
        return f"{float(value):.1f}%"
    except Exception:
        return "n.a."


def get_weekly_data(region):
    data = load_json(weekly_sources.get(region, []))
    return data if isinstance(data, dict) else {}


def get_hotspot_data(region):
    data = load_json(hotspot_sources.get(region, []))
    return data if isinstance(data, dict) else {}


def get_event_counts():
    results = {}

    for region in weekly_sources:
        data = get_weekly_data(region)
        counts = data.get("counts", {})
        results[region] = sum_numeric_values(counts) if isinstance(counts, dict) else 0

    return results


def get_top_hotspots(region, limit=3):
    data = get_hotspot_data(region)
    hotspots = data.get("top", [])
    if not isinstance(hotspots, list):
        return []
    return hotspots[:limit]


def extract_key_points(data, limit=3):
    bullets = [clean_text(x) for x in ensure_list(data.get("bullets")) if clean_text(x)]
    if bullets:
        return bullets[:limit]

    fallback = []
    for key in ["weekly_assessment", "risk_assessment", "forecast", "external_actors"]:
        txt = clean_text(data.get(key, ""))
        if txt:
            fallback.append(clip_text(txt, 260))
    return fallback[:limit]


def get_source_mix_text(counts):
    if not isinstance(counts, dict):
        return (
            "A forrásösszetétel nem áll rendelkezésre.",
            "Source composition is not available."
        )

    ranked = sorted(
        [(k, safe_int(v, 0)) for k, v in counts.items() if safe_int(v, 0) > 0],
        key=lambda x: x[1],
        reverse=True
    )

    if not ranked:
        return (
            "A forrásösszetétel nem áll rendelkezésre.",
            "Source composition is not available."
        )

    hu = "Forrásösszetétel: " + ", ".join([f"{name}: {value}" for name, value in ranked]) + "."
    en = "Source composition: " + ", ".join([f"{name}: {value}" for name, value in ranked]) + "."
    return hu, en


def get_top_country_scores(country_scores, limit=3):
    if not isinstance(country_scores, dict):
        return []

    pairs = []
    for country, metrics in country_scores.items():
        if isinstance(metrics, dict):
            pairs.append((country, safe_float(metrics.get("total", 0), 0.0)))

    pairs.sort(key=lambda x: x[1], reverse=True)
    return pairs[:limit]


def render_country_scores(country_scores, limit=3):
    top = get_top_country_scores(country_scores, limit=limit)
    if not top:
        return (
            "nem áll rendelkezésre országkitettségi lista",
            "no country exposure ranking is available"
        )
    text = ", ".join([f"{country} ({score:.1f})" for country, score in top])
    return text, text


def detect_signal_type(sources):
    if not isinstance(sources, dict):
        return (
            "nem meghatározható jelzéstípus",
            "unclassified signal"
        )

    gdelt = safe_int(sources.get("GDELT", 0))
    gdelt_doc = safe_int(sources.get("GDELT_DOC", 0))
    direct_feed = safe_int(sources.get("DIRECT_FEED", 0))
    usgs = safe_int(sources.get("USGS", 0))
    gdacs = safe_int(sources.get("GDACS", 0))

    political_total = gdelt + gdelt_doc + direct_feed
    hazard_total = usgs + gdacs

    if political_total > 0 and hazard_total == 0:
        if gdelt_doc > gdelt and gdelt_doc >= direct_feed:
            return (
                "dokumentum- és médiamonitoring alapú biztonsági jelzés",
                "document and media monitoring-based security signal"
            )
        if direct_feed > gdelt + gdelt_doc:
            return (
                "közvetlen feed-alapú incidensjelzés",
                "direct-feed based incident signal"
            )
        return (
            "hír- és politikai-biztonsági monitorozási jelzés",
            "news and political-security monitoring signal"
        )

    if hazard_total > 0 and political_total == 0:
        if usgs > 0 and gdacs > 0:
            return (
                "összetett természeti veszélyhelyzeti jelzés",
                "composite natural hazard signal"
            )
        if usgs > 0:
            return (
                "szeizmikus eseményjelzés",
                "seismic activity signal"
            )
        return (
            "katasztrófa-riasztási jelzés",
            "disaster alert signal"
        )

    if political_total > 0 and hazard_total > 0:
        return (
            "összetett, több forrásdoménből származó jelzés",
            "multi-domain composite signal"
        )

    return (
        "vegyes vagy korlátozottan azonosítható jelzés",
        "mixed or weakly identifiable signal"
    )


def hotspot_type_label(sources):
    if not isinstance(sources, dict):
        return "Vegyes / Mixed"

    gdelt = safe_int(sources.get("GDELT", 0))
    gdelt_doc = safe_int(sources.get("GDELT_DOC", 0))
    direct_feed = safe_int(sources.get("DIRECT_FEED", 0))
    usgs = safe_int(sources.get("USGS", 0))
    gdacs = safe_int(sources.get("GDACS", 0))

    political_total = gdelt + gdelt_doc + direct_feed
    hazard_total = usgs + gdacs

    if political_total > 0 and hazard_total == 0:
        if gdelt_doc > gdelt and gdelt_doc >= direct_feed:
            return "Dokumentum- és médiavezérelt biztonsági gócpont / Document-driven security hotspot"
        if direct_feed > gdelt + gdelt_doc:
            return "Feed-alapú incidensgóc / Direct-feed incident hotspot"
        return "Politikai / biztonsági incidensjelzés / Political-security incident signal"

    if hazard_total > 0 and political_total == 0:
        if usgs > 0 and gdacs > 0:
            return "Természeti veszélyhelyzet / Natural hazard"
        if usgs > 0:
            return "Szeizmikus aktivitás / Seismic activity"
        return "Katasztrófa-riasztás / Disaster alert"

    if political_total > 0 and hazard_total > 0:
        return "Összetett biztonsági jelzés / Composite security signal"

    return "Vegyes / Mixed"


def hotspot_analysis_paragraphs(hotspot):
    place = hotspot.get("place", "Ismeretlen helyszín")
    count = safe_int(hotspot.get("count", 0))
    trend = str(hotspot.get("trend", "stable")).lower()
    change_pct = format_change_pct(hotspot.get("change_pct", 0))
    score = safe_float(hotspot.get("score", 0))
    sources = hotspot.get("sources", {})

    signal_type_hu, signal_type_en = detect_signal_type(sources)
    label = hotspot_type_label(sources)

    if trend == "up":
        trend_hu = "növekvő aktivitás figyelhető meg"
        trend_en = "an upward trend in activity can be observed"
    elif trend == "down":
        trend_hu = "az aktivitás mérséklődése figyelhető meg"
        trend_en = "a declining trend in activity can be observed"
    elif trend == "new":
        trend_hu = "újonnan megjelent aktivitás rajzolódik ki"
        trend_en = "newly emerging activity is visible"
    else:
        trend_hu = "az aktivitás viszonylag stabil képet mutat"
        trend_en = "activity appears relatively stable"

    if count >= 1000 or score >= 700:
        density_hu = "rendkívül magas eseménysűrűséget"
        density_en = "an exceptionally high event density"
    elif count >= 300 or score >= 150:
        density_hu = "magas eseménysűrűséget"
        density_en = "a high event density"
    elif count >= 80 or score >= 50:
        density_hu = "érzékelhető eseménysűrűséget"
        density_en = "a noticeable event density"
    else:
        density_hu = "korlátozott, de releváns aktivitást"
        density_en = "limited but relevant activity"

    paragraph_hu = (
        f"**{place}**  \n"
        f"Az elmúlt időszak fejleményei alapján {place} térségében {trend_hu}. "
        f"A monitoring rendszer {density_hu} azonosított, az aktivitásváltozás mértéke **{change_pct}**, "
        f"míg a hotspot intenzitási pontszáma **{score:.3f}**. "
        f"A jelenlegi jelzések elsődlegesen **{signal_type_hu}** formájában jelentkeznek.  \n"
        f"Jelzés típusa: **{label}**. "
        f"A rövid távú kilátások alapján a térség továbbra is releváns fókuszpont maradhat a regionális monitoring számára."
    )

    paragraph_en = (
        f"**{place}**  \n"
        f"Recent developments suggest that {trend_en} in the {place} area. "
        f"The monitoring system detected {density_en}, while the change in activity reached **{change_pct}** "
        f"and the hotspot intensity score stands at **{score:.3f}**. "
        f"Current signals are primarily identified as **{signal_type_en}**.  \n"
        f"Signal type: **{label}**. "
        f"Based on current trends, the location is likely to remain a relevant focal point for regional monitoring in the short term."
    )

    return paragraph_hu, paragraph_en


def build_hotspot_section():
    sections = []

    for region in hotspot_sources:
        hotspots = get_top_hotspots(region, limit=3)

        sections.append(f"### {region}")

        if not hotspots:
            sections.append("Nem áll rendelkezésre értékelhető hotspot adat.\n")
            sections.append("No evaluable hotspot data is currently available.\n")
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
    data = load_json(middle_east_events_paths)
    if not isinstance(data, list):
        return [], 0

    total = len(data)

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
    title = clean_text(event.get("title", "Untitled event"))
    summary = clip_text(event.get("summary", ""), 360)
    category = clean_text(event.get("category", "other"))
    confidence = safe_float(event.get("confidence", 0), 0.0)
    date = clean_text(event.get("date", "n.a."))

    source = event.get("source", {}) if isinstance(event.get("source", {}), dict) else {}
    source_name = clean_text(source.get("name", "Unknown source"))

    location = event.get("location", {}) if isinstance(event.get("location", {}), dict) else {}
    location_name = clean_text(location.get("name", "Middle East"))

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
        f"Az esemény **{signal_hu}** kategóriába sorolható, és a monitoring rendszer **{confidence:.2f}** bizalmi szint mellett kezelte. "
        f"A rendelkezésre álló összefoglaló alapján ez egy **{category_hu}**, amely hozzájárul a térség folyamatos stratégiai bizonytalanságához. "
        f"{summary}"
    )

    paragraph_en = (
        f"**{title}**  \n"
        f"Date: **{date}** | Location: **{location_name}** | Source: **{source_name}**  \n"
        f"This event can be classified as a **{signal_en}**, and it was handled by the monitoring system with a confidence level of **{confidence:.2f}**. "
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


def build_executive_summary(event_results, middle_east_total):
    balkan = get_weekly_data("Balkán")
    cee = get_weekly_data("Közép- és Kelet-Európa")

    balkan_points = extract_key_points(balkan, limit=2)
    cee_points = extract_key_points(cee, limit=2)

    total_events = (
        event_results.get("Balkán", 0)
        + event_results.get("Közép- és Kelet-Európa", 0)
        + middle_east_total
    )

    lines = []
    lines.append("# 1. Vezetői összefoglaló")
    lines.append("## Executive Summary")
    lines.append("")
    lines.append(
        f"Az aktuális ciklusban a monitoring rendszer **{total_events} biztonsági relevanciájú eseményt** azonosított a vizsgált régiókban. "
        f"A Balkánból **{event_results.get('Balkán', 0)}**, Közép- és Kelet-Európából **{event_results.get('Közép- és Kelet-Európa', 0)}**, "
        f"a Közel-Kelethez kapcsolódó streamből pedig **{middle_east_total}** tétel került a rendszerbe."
    )
    lines.append("")
    lines.append(
        f"In the current cycle, the monitoring system identified **{total_events} security-relevant items** across the observed regions. "
        f"Of these, **{event_results.get('Balkán', 0)}** were linked to the Balkans, "
        f"**{event_results.get('Közép- és Kelet-Európa', 0)}** to Central and Eastern Europe, "
        f"and **{middle_east_total}** to the Middle East stream."
    )
    lines.append("")
    lines.append(
        "Az összkép alapján nem egyetlen domináns válságpont rajzolódik ki, hanem több párhuzamos nyomáspont: "
        "politikai polarizáció, lokalizált biztonsági incidensek, információs nyomásgyakorlás és stratégiai bizonytalanság."
    )
    lines.append("")
    lines.append(
        "The overall picture does not suggest a single dominant crisis point, but rather multiple parallel pressure areas: "
        "political polarization, localized security incidents, information pressure and strategic uncertainty."
    )
    lines.append("")

    if balkan_points:
        lines.append("**Balkán:** " + " ".join([clip_text(x, 220) for x in balkan_points]))
        lines.append("")
        lines.append("**Balkans:** " + " ".join([clip_text(x, 220) for x in balkan_points]))
        lines.append("")
    if cee_points:
        lines.append("**Közép- és Kelet-Európa:** " + " ".join([clip_text(x, 220) for x in cee_points]))
        lines.append("")
        lines.append("**Central and Eastern Europe:** " + " ".join([clip_text(x, 220) for x in cee_points]))
        lines.append("")

    lines.append(
        "A jelenlegi trendek alapján rövid távon inkább tartós, alacsonyabb intenzitású, de politikailag érzékeny biztonsági környezet valószínűsíthető, "
        "mintsem hirtelen, minden térséget egyszerre érintő eszkaláció."
    )
    lines.append("")
    lines.append(
        "Current trends suggest a persistent, lower-intensity but politically sensitive security environment in the short term, "
        "rather than a sudden simultaneous escalation across all theatres."
    )
    lines.append("")

    return "\n".join(lines)


def build_current_security_section(event_results, middle_east_total, middle_east_section):
    lines = []
    lines.append("# 2. Aktuális biztonsági helyzet")
    lines.append("## Current Security Situation")
    lines.append("")
    lines.append("### Politikai környezet / Political Environment")
    lines.append("")
    lines.append(
        "A térség politikai rendszerei formális stabilitást mutatnak, ugyanakkor több országban erősödik a polarizáció, "
        "a társadalmi mobilizáció és a belpolitikai feszültségek biztonsági hatása."
    )
    lines.append("")
    lines.append(
        "Political systems across the monitored regions show formal stability, yet polarization, social mobilization and the security effects of domestic tensions are becoming more visible in several states."
    )
    lines.append("")
    lines.append("### Katonai és biztonsági helyzet / Military and Security Situation")
    lines.append("")
    lines.append(f"Balkán régióban azonosított események száma: **{event_results.get('Balkán', 0)}**  ")
    lines.append(f"Közép- és Kelet-Európában azonosított események száma: **{event_results.get('Közép- és Kelet-Európa', 0)}**  ")
    lines.append(f"Közel-Kelethez kapcsolódó azonosított események száma: **{middle_east_total}**")
    lines.append("")
    lines.append(
        "Az incidensek többsége továbbra is alacsony vagy közepes intenzitású biztonsági fejleményekhez, politikai feszültségekhez, "
        "lokalizált gócpontokhoz vagy stratégiai jelentőségű híralapú eseményekhez kapcsolódik."
    )
    lines.append("")
    lines.append(
        "Most detected items remain linked to low- or medium-intensity security developments, political tensions, localized hotspots or strategically relevant news-based events."
    )
    lines.append("")
    lines.append(middle_east_section)
    lines.append("")
    return "\n".join(lines)


def build_geopolitical_section():
    return """# 3. Geopolitikai környezet
## Geopolitical Environment

A térség geopolitikai jelentősége abból fakad, hogy stratégiai energia-, kereskedelmi és politikai útvonalak találkozási pontjában helyezkedik el. A jelenlegi dinamikát a nagyhatalmi versengés, a regionális biztonsági architektúra változásai és a gazdasági alkalmazkodóképesség kérdései alakítják.

The geopolitical relevance of the broader area stems from its position along strategic energy, trade and political corridors. Current dynamics are shaped by great-power competition, changing security architectures and questions of economic resilience.
"""


def build_challenges_section():
    return """# 4. Fő biztonsági kihívások
## Main Security Challenges

A legjelentősebb kockázatot jelenleg az jelenti, hogy több térségben egyszerre jelentkeznek politikai, gazdasági, információs és biztonsági természetű kihívások. A hibrid hadviselés elemei, különösen az információs műveletek és a kibertérhez kapcsolódó sérülékenységek, továbbra is fontos kockázati tényezők.

The most significant current risk lies in the simultaneous presence of political, economic, information and security pressures across multiple monitored areas. Hybrid elements, especially information operations and cyber-related vulnerabilities, remain important risk factors.
"""


def build_region_context_section():
    lines = []
    lines.append("# 5. Régiós értelmezés")
    lines.append("## Regional Analytical Context")
    lines.append("")

    for region in weekly_sources:
        data = get_weekly_data(region)
        if not data:
            continue

        headline = clean_text(data.get("headline", region))
        assessment = clip_text(data.get("weekly_assessment", ""), 600)
        risk = clip_text(data.get("risk_assessment", ""), 420)
        forecast = clip_text(data.get("forecast", ""), 420)
        counts = data.get("counts", {})
        country_scores = data.get("country_scores", {})

        source_mix_hu, source_mix_en = get_source_mix_text(counts)
        exposure_hu, exposure_en = render_country_scores(country_scores, limit=3)

        lines.append(f"### {region}")
        lines.append("")
        if headline:
            lines.append(f"**{headline}**")
            lines.append("")

        if assessment:
            lines.append(assessment)
            lines.append("")
            lines.append(assessment)
            lines.append("")

        lines.append(
            f"A régióban mért összesített heti eseménymennyiség: **{sum_numeric_values(counts)}**. "
            f"A legmagasabb súlyozott országkitettségek: **{exposure_hu}**."
        )
        lines.append("")
        lines.append(
            f"Total weekly event volume in the region: **{sum_numeric_values(counts)}**. "
            f"Highest weighted country exposures: **{exposure_en}**."
        )
        lines.append("")
        lines.append(source_mix_hu)
        lines.append("")
        lines.append(source_mix_en)
        lines.append("")

        if risk:
            lines.append(f"**Kockázati értékelés:** {risk}")
            lines.append("")
            lines.append(f"**Risk assessment:** {risk}")
            lines.append("")

        if forecast:
            lines.append(f"**Rövid távú előretekintés:** {forecast}")
            lines.append("")
            lines.append(f"**Short-term outlook:** {forecast}")
            lines.append("")

    return "\n".join(lines)


def build_risk_table_section():
    return """# 6. Kockázatelemzés
## Risk Assessment

| Fenyegetés | Valószínűség | Hatás | Kockázati szint |
|---|---|---|---|
| Határincidensek | magas | közepes | magas |
| Politikai instabilitás | közepes | magas | magas |
| Hibrid műveletek | magas | közepes | magas |
| Nagyhatalmi versengés | közepes | magas | magas |
| Energiapiaci zavarok | közepes | magas | magas |

| Threat | Probability | Impact | Risk level |
|---|---|---|---|
| Border incidents | high | medium | high |
| Political instability | medium | high | high |
| Hybrid operations | high | medium | high |
| Great-power competition | medium | high | high |
| Energy-market disruption | medium | high | high |
"""


def build_forecast_section():
    return """# 7. Előrejelzés
## Forecast

A jelenlegi trendek alapján rövid távon fennmaradhat az alacsonyabb intenzitású, de tartós biztonsági nyomás, miközben a Közel-Kelethez kapcsolódó fejlemények közvetett hatást gyakorolhatnak a tágabb regionális környezetre. A geopolitikai rivalizálás erősödése miatt a vizsgált térség továbbra is stratégiai jelentőségű biztonsági tér marad.

Current trends suggest that lower-intensity but persistent security pressure is likely to continue in the short term, while developments linked to the Middle East may continue to shape the broader environment indirectly. As geopolitical rivalry intensifies, the monitored space is likely to remain strategically relevant.
"""


def build_recommendations_section():
    return """# 8. Ajánlások
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
"""


def build_methodology_section():
    return """# 9. Módszertan és adatforrások
## Methodology and Data Sources

A jelentés automatizált monitoring rendszerekből származó adatok feldolgozásán alapul. A jelenlegi verzió heti összesítésekre, hotspot-jelzésekre és a Közel-Kelethez kapcsolódó eseménylistákra épül. A brief kiegészítő elemző szövegeket is felhasznál, amennyiben azok elérhetők a régiós weekly állományokban.

This report is based on automated monitoring outputs. The current version relies on weekly aggregation files, hotspot signal summaries and Middle East event lists. Where available, the brief also uses analytical text fields from regional weekly files.

Adatforrások / Data sources:

- Balkan Security Map  
- CEE Security Map  
- Middle East Security Monitor
"""


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

executive_summary = build_executive_summary(event_results, middle_east_total)
current_security = build_current_security_section(event_results, middle_east_total, middle_east_section)
geopolitical = build_geopolitical_section()
challenges = build_challenges_section()
region_context = build_region_context_section()
risk_table = build_risk_table_section()
forecast = build_forecast_section()
recommendations = build_recommendations_section()
methodology = build_methodology_section()

report = f"""# REGIONÁLIS BIZTONSÁGPOLITIKAI HELYZETJELENTÉS
# REGIONAL SECURITY SITUATION REPORT

## Visual Overview

### Top Hotspot Growth Rate
![Hotspot Growth Chart](growth_chart.png)

Balkán – Közép- és Kelet-Európa – Közel-Kelet  
Balkans – Central and Eastern Europe – Middle East  

Készítés dátuma: {date_hu}  
Date of issue: {date_en}  

Terjesztés: Nyilvános elemzés  
Distribution: Public analysis  

Készítette: toresvonalak.blog  
Prepared by: toresvonalak.blog  

---

{executive_summary}

---

{current_security}

---

{geopolitical}

---

{challenges}

---

{region_context}

---

# 5/A. Regionális hotspotok
## Regional Hotspots

{hotspot_section}

---

{risk_table}

---

{forecast}

---

{recommendations}

---

{methodology}
"""

with open("report.md", "w", encoding="utf-8") as f:
    f.write(report)

print("Security report generated successfully")

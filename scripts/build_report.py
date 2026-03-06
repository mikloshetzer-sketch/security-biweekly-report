import os
import json
from datetime import datetime

sources = {
    "Balkán": "balkan-security-map/docs/data/weekly.json",
    "Közép- és Kelet-Európa": "cee-security-map/data/weekly.json"
}

results = {}

for region, path in sources.items():
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        results[region] = len(data)
    else:
        results[region] = 0

total_events = sum(results.values())

date_hu = datetime.utcnow().strftime("%Y. %B %d")
date_en = datetime.utcnow().strftime("%Y-%m-%d")

report = f"""
# REGIONÁLIS BIZTONSÁGPOLITIKAI HELYZETJELENTÉS
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

Az elmúlt időszak fejleményei arra utalnak, hogy a megfigyelt régiókban továbbra is fennmaradnak a biztonsági kockázatok, különösen a regionális politikai feszültségek és határmenti incidensek tekintetében.

A monitoring rendszer az aktuális időszakban **{total_events} biztonsági relevanciájú eseményt** azonosított a vizsgált régiókban.

A jelenlegi trendek alapján valószínűsíthető, hogy a Balkán és a közép-kelet-európai térségben alacsony intenzitású, de tartós biztonsági incidensek továbbra is jelen lesznek.

Bár közvetlen katonai konfliktus nem várható, a helyzet továbbra is fokozott figyelmet igényel a regionális biztonságpolitikai döntéshozók részéről.

---

# 2. Aktuális biztonsági helyzet  
## Current Security Situation

### Politikai környezet

A térség politikai rendszerei jelenleg relatív stabilitást mutatnak, ugyanakkor több országban megfigyelhető a politikai polarizáció erősödése és a társadalmi mobilizáció növekedése.

### Katonai helyzet

Balkán régióban azonosított események száma: **{results["Balkán"]}**

Közép- és Kelet-Európában azonosított események száma: **{results["Közép- és Kelet-Európa"]}**

Az incidensek többsége alacsony intenzitású eseményekhez, politikai feszültségekhez vagy biztonsági incidensekhez kapcsolódik.

---

# 3. Geopolitikai környezet  
## Geopolitical Environment

A térség geopolitikai jelentősége elsősorban abból fakad, hogy a régió több stratégiai jelentőségű energia- és kereskedelmi útvonal metszéspontjában helyezkedik el.

A jelenlegi geopolitikai dinamikát a nagyhatalmi versengés, a regionális biztonsági architektúra változásai és a gazdasági stabilitás kérdései alakítják.

---

# 4. Fő biztonsági kihívások  
## Main Security Challenges

A legjelentősebb kockázatot jelenleg az jelenti, hogy több térségben egyszerre jelentkeznek politikai, gazdasági és biztonsági jellegű kihívások.

A térségben az utóbbi időszakban erősödtek a hibrid hadviselés elemei, különösen az információs műveletek és a kibertámadások területén.

---

# 5. Kockázatelemzés  
## Risk Assessment

| Fenyegetés | Valószínűség | Hatás | Kockázati szint |
|---|---|---|---|
| Határincidensek | magas | közepes | magas |
| Politikai instabilitás | közepes | magas | magas |
| Hibrid műveletek | magas | közepes | magas |
| Nagyhatalmi versengés | közepes | magas | magas |

---

# 6. Előrejelzés  
## Forecast

A jelenlegi trendek alapján valószínűsíthető, hogy a régiókban rövid távon fennmarad az alacsony intenzitású biztonsági feszültség.

A geopolitikai rivalizálás erősödése következtében a térség továbbra is stratégiai jelentőségű biztonsági térként jelenik meg.

---

# 7. Ajánlások  
## Recommendations

A regionális stabilitás fenntartása érdekében a következő lépések javasoltak:

- a határ menti katonai kommunikáció erősítése  
- a bizalomépítő intézkedések kiterjesztése  
- a dezinformáció elleni együttműködés növelése  
- a gazdasági stabilitást támogató nemzetközi programok bővítése  

---

# 8. Módszertan és adatforrások  
## Methodology and Data Sources

A jelentés automatizált monitoring rendszerekből származó adatok feldolgozásán alapul.

Adatforrások:

- Balkan Security Map  
- CEE Security Map  
- Middle East Security Monitor
"""

with open("report.md", "w", encoding="utf-8") as f:
    f.write(report)

print("Security report generated successfully")

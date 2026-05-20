from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup


SOURCES = [
    "https://www.ttsbooking.tn/voyages-organises/",
    "https://www.voyagetunisie.tn/voyages-de-noces/istanbul.html",
    "https://www.cte.tn/voyage/voyage-istanbul-2026.html",
    "https://www.hotelstunisie.tn/voyages",
    "https://www.omra24.com/",
    "https://www.omratunisie.tn/omra/sup.html",
    "https://tp.octasoft.com.tn/",
]

DESTINATIONS = ["Istanbul", "Dubai", "Paris", "La Mecque", "Marrakech", "Antalya", "Le Caire", "Rome", "Omra"]
PRICE_RE = re.compile(r"(?:(?:à partir de|a partir de|dès|des)\s*)?([0-9][0-9\s.,]{2,})\s*(?:TND|DT|dinars?)", re.I)
DURATION_RE = re.compile(r"([0-9]{1,2})\s*(?:jours?|j)\s*(?:/|\&|et)?\s*([0-9]{1,2})?\s*(?:nuits?|n)?", re.I)


def scrape_public_sources(output_path: str | Path, timeout: int = 15) -> list[dict[str, Any]]:
    """Best-effort scraper for public agency pages.

    Many travel websites render offers client-side or block automated requests, so
    this function stores whatever can be extracted and lets trainer.py use its
    curated fallback data when pages are unavailable.
    """
    offers: list[dict[str, Any]] = []
    headers = {"User-Agent": "Mozilla/5.0 Rihla-AI academic recommender bot"}
    for url in SOURCES:
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            offers.append({"source_url": url, "status": "failed", "error": str(exc)})
            continue

        text = BeautifulSoup(response.text, "html.parser").get_text(" ", strip=True)
        chunks = [text[max(0, match.start() - 180): match.end() + 180] for match in PRICE_RE.finditer(text)]
        for chunk in chunks[:30]:
            destination = next((dest for dest in DESTINATIONS if dest.lower() in chunk.lower()), None)
            price_match = PRICE_RE.search(chunk)
            duration_match = DURATION_RE.search(chunk)
            if not price_match:
                continue
            price = float(price_match.group(1).replace(" ", "").replace(".", "").replace(",", "."))
            offers.append({
                "source_url": url,
                "status": "ok",
                "destination": destination,
                "price_tnd": price,
                "duration_days": int(duration_match.group(1)) if duration_match else None,
                "raw_excerpt": chunk[:500],
            })

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(offers, ensure_ascii=False, indent=2), encoding="utf-8")
    return offers

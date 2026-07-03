"""
Best-effort scraper for Quantpedia's free strategy listing.

IMPORTANT: Quantpedia's site structure can change, and much of its content
sits behind Premium/Pro paywalls. This scraper only targets the free-tier
strategy list page. If it returns zero results, the site has likely changed
its markup — open the URL manually, inspect the strategy card element, and
update SELECTOR_CONFIG below rather than assuming the pipeline is broken.
"""
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ideas-intake-bot/1.0; personal research use)"
}

# Adjust these if quantpedia.com changes its DOM
SELECTOR_CONFIG = {
    "card": "div.strategy-item, article.strategy, div.screener-item",
    "title": "h2, h3, .strategy-title, a.title",
    "link": "a",
}


def fetch_quantpedia(free_strategies_url: str) -> list[dict]:
    entries = []
    try:
        resp = requests.get(free_strategies_url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"[quantpedia] WARNING: fetch failed ({e}). Skipping — pull ideas manually from {free_strategies_url}")
        return entries

    soup = BeautifulSoup(resp.text, "lxml")
    cards = soup.select(SELECTOR_CONFIG["card"])

    if not cards:
        print("[quantpedia] WARNING: no strategy cards found with current selectors.")
        print("  -> Site markup likely changed, or content is JS-rendered client-side.")
        print(f"  -> Manually check {free_strategies_url} and update SELECTOR_CONFIG in quantpedia_source.py")
        return entries

    for card in cards:
        title_el = card.select_one(SELECTOR_CONFIG["title"])
        link_el = card.select_one(SELECTOR_CONFIG["link"])

        title = title_el.get_text(strip=True) if title_el else None
        link = link_el.get("href") if link_el else None

        if not title:
            continue

        if link and link.startswith("/"):
            link = "https://quantpedia.com" + link

        entries.append({
            "source": "quantpedia",
            "category": "strategy_db",
            "title": title,
            "url": link or free_strategies_url,
            "published": None,
            "summary": "",  # free tier rarely exposes full description in the listing
        })

    return entries

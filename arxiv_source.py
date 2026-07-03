"""
Pulls recent papers from arXiv q-fin categories via the public Atom API.
No auth needed. http://export.arxiv.org/api/query
"""
import feedparser
import time
from urllib.parse import quote


ARXIV_API = "http://export.arxiv.org/api/query"


def fetch_arxiv(categories: list[str], max_results_per_category: int, keyword_filter: list[str]) -> list[dict]:
    entries = []
    kw_lower = [k.lower() for k in keyword_filter]

    for cat in categories:
        query = f"search_query=cat:{cat}&sortBy=submittedDate&sortOrder=descending&max_results={max_results_per_category}"
        url = f"{ARXIV_API}?{query}"

        try:
            feed = feedparser.parse(url)
        except Exception as e:
            print(f"[arxiv] WARNING: failed to fetch {cat}: {e}")
            continue

        if not feed.entries:
            print(f"[arxiv] WARNING: no entries returned for {cat} (check category code or connectivity)")
            continue

        for item in feed.entries:
            title = item.get("title", "").replace("\n", " ").strip()
            summary = item.get("summary", "").replace("\n", " ").strip()

            haystack = (title + " " + summary).lower()
            if kw_lower and not any(k in haystack for k in kw_lower):
                continue

            entries.append({
                "source": "arxiv",
                "category": cat,
                "title": title,
                "url": item.get("link", ""),
                "published": item.get("published", "")[:10],
                "summary": summary[:600],  # trim for token efficiency downstream
            })

        time.sleep(1)  # be polite to arXiv's rate limits

    return entries

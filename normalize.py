"""
Dedupes raw entries and tags them against your live BRUTEFORCE strategy
families (from config.yaml: strategy_tag_map) so triage is faster.
"""
import hashlib


def _entry_hash(entry: dict) -> str:
    key = (entry.get("title", "") + entry.get("url", "")).lower().strip()
    return hashlib.md5(key.encode()).hexdigest()


def dedupe(entries: list[dict]) -> list[dict]:
    seen = set()
    out = []
    for e in entries:
        h = _entry_hash(e)
        if h in seen:
            continue
        seen.add(h)
        out.append(e)
    return out


def tag_entries(entries: list[dict], strategy_tag_map: dict) -> list[dict]:
    for e in entries:
        haystack = (e.get("title", "") + " " + e.get("summary", "")).lower()
        related = []
        for strategy, keywords in strategy_tag_map.items():
            if any(kw.lower() in haystack for kw in keywords):
                related.append(strategy)
        e["related_strategies"] = related
        e["status"] = "intake"  # pending your own fresh IS/OOS test — not a validated edge yet
    return entries

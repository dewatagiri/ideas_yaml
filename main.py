"""
Run: python main.py

Pulls candidate alpha ideas from arXiv q-fin + Quantpedia free strategies,
tags them against your BRUTEFORCE strategy families, and writes ideas.yaml
for intake. Nothing here is backtested — status is always "intake" until
you run it through your own IS/OOS split.
"""
import yaml
from datetime import datetime, timezone

from arxiv_source import fetch_arxiv
from quantpedia_source import fetch_quantpedia
from normalize import dedupe, tag_entries


def load_config(path: str = "config.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    cfg = load_config()
    all_entries = []

    if cfg["arxiv"]["enabled"]:
        print("[main] fetching arXiv q-fin...")
        arxiv_entries = fetch_arxiv(
            categories=cfg["arxiv"]["categories"],
            max_results_per_category=cfg["arxiv"]["max_results_per_category"],
            keyword_filter=cfg["arxiv"]["keyword_filter"],
        )
        print(f"[main]   -> {len(arxiv_entries)} matched entries")
        all_entries.extend(arxiv_entries)

    if cfg["quantpedia"]["enabled"]:
        print("[main] fetching Quantpedia free strategies...")
        qp_entries = fetch_quantpedia(cfg["quantpedia"]["free_strategies_url"])
        print(f"[main]   -> {len(qp_entries)} entries")
        all_entries.extend(qp_entries)

    all_entries = dedupe(all_entries)
    all_entries = tag_entries(all_entries, cfg["strategy_tag_map"])

    # stable IDs for referencing in BRUTEFORCE's own tracking later
    for i, e in enumerate(all_entries, start=1):
        e["id"] = f"idea-{i:04d}"

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(all_entries),
        "ideas": all_entries,
    }

    out_path = cfg["output_path"]
    with open(out_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(output, f, sort_keys=False, allow_unicode=True, width=100)

    print(f"[main] wrote {len(all_entries)} ideas to {out_path}")

    tagged = [e for e in all_entries if e["related_strategies"]]
    print(f"[main] {len(tagged)} entries auto-tagged to an existing strategy family")


if __name__ == "__main__":
    main()

# ideas_intake

Pulls alpha ideas from academic/strategy databases and writes a structured
`ideas.yaml` for BRUTEFORCE intake. Nothing here is backtested — every entry
gets `status: intake` until you run it through your own fresh IS/OOS split.

## What this actually does

It's a scout. Every run, it goes out to arXiv (the free repository where
quant/finance academics post papers) and pulls the newest papers on trading,
market structure, and portfolio strategies. It flags which ones look related
to strategies you already run (Bernard, SSL-AR, DBB, Alpha Hunter, ORB FX,
on-chain). You get a shortlist of candidate ideas without manually browsing
arXiv yourself.

## Where the benefit is

Without this, your idea pipeline is: whatever you personally think of, or
stumble across. That's a narrow funnel — you're one person.

With this, you've got a standing feed of peer-reviewed-adjacent research
constantly generating candidate hypotheses, pre-filtered to what's plausibly
relevant to what you already trade. It doesn't replace your judgment or your
backtesting rigor — it widens the top of the funnel so more ideas reach the
backtest stage without you having to go find them yourself.

Realistic cadence: run weekly, spend 10 minutes triaging, maybe 1 idea a
month actually makes it into a real backtest. That's still a net positive
over zero external idea sourcing.

## Step by step

**1. Run it**
```
cd D:\ideas_yaml
python main.py
```
Takes ~30 seconds. Writes/overwrites `ideas.yaml` in this folder.

**2. Open the file**
Open `ideas.yaml` in VS Code or Notepad. Each entry has a title, summary,
link, and which of your strategies it might relate to (`related_strategies`).

**3. Skim it (5-10 min)**
Read the titles. For each: does this sound like a real edge, or noise? Most
will be irrelevant — that's normal. You're looking for the 1-3 that make you
stop and read closer.

**4. Pick one and dig deeper**
Click the `url`, read the abstract on arXiv. Is this actually testable with
data you have (Bybit, MT5, yfinance, etc.)?

**5. Hand it off to build**
Open a fresh chat (or Antigravity/Claude Code session) and paste just that
one entry — title + summary + link. Ask for it to be turned into a testable
hypothesis and backtested with your usual IS/OOS + walk-forward discipline.
Don't trust any performance numbers in the source paper — those are the
authors' in-sample result, not yours.

**6. It survives or dies**
Same as every other strategy in your pipeline. Clears OOS → new BRUTEFORCE
candidate. Doesn't → killed cheaply, a few hours spent instead of weeks.

**7. Track state**
Update `status:` in ideas.yaml as you go (`intake` → `reading` → `promoted`
/ `killed`). When a literature idea seeds a real strategy, note the origin
in that strategy's `summary.md` — e.g. "Origin: idea-0009 (Hyperliquid
sunshine trading, arXiv 2606.15715)" — so you can trace back later.

## Example: turning one idea into a backtest brief

Walkthrough using an idea pulled from this pipeline's own output, as a
template for how to write up any future entry before handing it to a fresh
BRUTEFORCE chat.

> **Source:** arXiv 2606.29591, "The Bounce Has No Direction: Sign,
> Magnitude, and the Microstructure of Equity Return Predictability" —
> https://arxiv.org/abs/2606.29591v1 (pulled via this pipeline's arXiv
> scraper, idea-0003)
>
> **Caveat — do your own backtesting.** Everything below is a hypothesis
> derived from reading the abstract, not a validated result. All performance
> claims belong to the paper's authors, on their data, with their
> methodology. None of it has been run through IBOT (IS/OOS split,
> walk-forward, cost-realistic execution). Treat this strictly as a starting
> hypothesis to test fresh — not as evidence of an edge.
>
> **Hypothesis to test:** SPY (or BTC) may show significant negative lag-1
> daily return autocorrelation — a large move today tends to be followed by
> a smaller-magnitude move tomorrow, but the *direction* of tomorrow's move
> may not be reliably predictable from today's sign alone. The edge, if any,
> may sit in volatility/magnitude prediction, not directional reversal.
>
> **Simple testable version:**
> 1. Compute daily returns for the target asset (BTC/ETH perp, or SPY as a
>    sanity check against the paper's own universe)
> 2. Split into sign bucket (up day / down day) and magnitude bucket
>    (top/bottom tercile by |return|)
> 3. Test: does next-day |return| shrink after a large-magnitude day,
>    regardless of sign? (magnitude channel)
> 4. Separately test: does next-day sign depend on today's sign? (sign
>    channel — the paper's claim implies this should be weak/absent)
> 5. If the magnitude channel holds OOS, treat it as a risk-sizing overlay
>    (reduce size / tighten stops after large moves), not a directional
>    entry signal
>
> **Validation plan:** IS 2018–2023, OOS 2024–2026, walk-forward if the
> magnitude effect survives. Cost-realistic backtest (low-frequency daily
> signal, so cost sensitivity should be minor — useful as a first sanity
> check on the framework itself).
>
> **What a negative result means:** if the magnitude effect doesn't hold on
> BTC, that's still informative — it may indicate the effect is specific to
> equity market microstructure rather than universal across assets. Not
> every idea in ideas.yaml needs to survive to be useful.



```
pip install -r requirements.txt --break-system-packages
python main.py
```

Output: `ideas.yaml` in this folder.

## Sources

**arXiv q-fin** — works out of the box. Public Atom API, no auth, no JS
rendering. Pulls q-fin.TR / q-fin.ST / q-fin.PM, filters by keyword_filter
in config.yaml.

**Quantpedia free strategies** — best-effort, and confirmed to 403/bot-block
requests without a browser session (tested during build). Two options:
1. If you have a Quantpedia account, swap `requests` for an authenticated
   session (cookies) in `quantpedia_source.py` — add your session cookie
   header there.
2. Skip scraping and pull ideas manually from https://quantpedia.com/strategies/
   — set `quantpedia.enabled: false` in config.yaml and just paste interesting
   strategies into ideas.yaml by hand using the same schema.

If you get Quantpedia Premium/Pro later, they expose an actual API — worth
switching quantpedia_source.py over to that instead of scraping once you have
a key (mentioned in their docs: "algorithmic access to the full Quantpedia
database via the API").

## Editing what gets pulled

All filtering knobs live in `config.yaml`:
- `arxiv.keyword_filter` — substring match against title+abstract
- `strategy_tag_map` — maps keyword phrases to your live strategy families
  (bernard_system, ssl_ar, dbb, btc_options_pinning, alpha_hunter_v2,
  orb_fx, on_chain) so new ideas get flagged as "related to X" automatically.
  Prefer multi-word phrases over single generic words (e.g. "regime
  classifier" not "regime") — single common words cause false-positive tags.

## ideas.yaml schema

```yaml
generated_at: <ISO timestamp>
count: <int>
ideas:
  - id: idea-0001
    source: arxiv | quantpedia
    category: <arxiv category or "strategy_db">
    title: <str>
    url: <str>
    published: <date or null>
    summary: <str, truncated to 600 chars>
    related_strategies: [bernard_system, ...]   # auto-tagged, may be empty
    status: intake
```

## Next step per idea

`status: intake` → pull into BRUTEFORCE → run your own fresh IS/OOS split
(do not trust any performance numbers in the source paper/listing — those
are someone else's in-sample result) → walk-forward → promote or kill.

## Files

- `config.yaml` — all tunables
- `arxiv_source.py` — arXiv Atom API fetcher
- `quantpedia_source.py` — best-effort scraper, fails gracefully with a
  clear warning if selectors break (site markup changes over time)
- `normalize.py` — dedup + strategy-family tagging
- `main.py` — orchestrator, run this


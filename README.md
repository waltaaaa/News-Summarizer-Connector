# News Summarizer & Connector

Pipeline that turns a news-article repository spreadsheet (8,926 articles: headline, source,
URL, date) into:

1. **An Obsidian vault** (`vault/`) — one markdown note per article with a 1–2 sentence
   summary, a one-sentence key takeaway, and wikilinks to keyword hub notes, so Obsidian's
   graph view shows the corpus clustered by theme.
2. **An enriched spreadsheet** (`output/articles_enriched.csv`) — the original columns plus
   summary, takeaway, keywords, and entities.

Keywords come from a **controlled taxonomy** (`taxonomy/taxonomy.json`, ~78 keywords) so tags
stay consistent across thousands of articles — and so a future second list of *insight
articles* can be tagged with the same vocabulary and connected through shared keyword hubs.

Everything runs inside **Claude Code on your subscription**: Python scripts (stdlib only)
handle the deterministic work; Claude spawns Haiku subagents to write summaries and assign
keywords. No API key required.

## Getting the results on your machine

Clone once:

```
git clone https://github.com/waltaaaa/News-Summarizer-Connector "C:\News Summarizer and Connector"
```

then `git pull` after each processing session. Open the `vault/` folder as an Obsidian vault
(Obsidian → Open folder as vault). In graph view, create color groups for `path:articles/news`,
`path:keywords` (and later `path:articles/insights`) to see the map.

## Usage (in a Claude Code session)

| Command | What it does |
|---|---|
| `/build-taxonomy` | Sample the corpus, propose the keyword vocabulary, freeze `taxonomy.json` after your review. Already done (v1, 78 keywords) — rerun only to revise. |
| `/process-articles 100` | Summarize + tag the next 100 pending articles (newest first). Fully resumable — run it as many times as you like, across sessions, until `pending: 0`. |

State lives in `data/ledger.jsonl` (append-only). `scripts/status.py` shows progress anytime.

## Content fetching

`scripts/fetch_content.py` tries to download each article's full text so summaries are
grounded in the actual article. When fetching fails (paywall, dead link, or — as in
Claude Code web sandboxes — no network egress at all), the article is summarized from its
headline, source, and date instead and flagged `content_basis: headline-only` in both the
note frontmatter and the CSV. Run sessions in a network-enabled environment to get
full-text grounding; refetch and reprocess later is always possible.

## Pipeline internals

```
xlsx ─ extract_articles.py ─▶ data/articles.jsonl      (canonical records, stable IDs)
            fetch_content.py ─▶ data/cache/<id>.json    (full text or error; gitignored)
              make_batch.py ─▶ data/batches/batch_*.json (25 articles each; gitignored)
        [Haiku subagent]    ─▶ data/batches/result_*.json
          ingest_results.py ─▶ data/ledger.jsonl + vault/articles/news/*.md + vault/keywords/*.md
             export_csv.py  ─▶ output/articles_enriched.csv
```

- **Stable IDs**: `n-<sha1(normalized url)[:12]>` — tracking params stripped, so re-imports
  and re-runs never duplicate. (30 duplicate spreadsheet rows were collapsed this way.)
- **Validation**: every subagent result is checked — keywords must resolve (case-insensitive,
  alias-aware) to the frozen taxonomy; malformed items are retried once, then marked
  `needs_review` in the ledger. The pipeline never wedges.

## Next phase (designed, not yet built)

- Ingest the **insight articles** list with `i-` IDs into `vault/articles/insights/`,
  tagged from the same taxonomy.
- `scripts/find_connectors.py`: rank keywords by (news backlinks × insight backlinks) and
  write `vault/connectors/<Keyword> connectors.md` reports — the bridges between the two maps.

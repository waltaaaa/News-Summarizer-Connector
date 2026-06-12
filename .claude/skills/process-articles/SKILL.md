---
name: process-articles
description: Summarize and tag the next N pending news articles from the repository spreadsheet using Haiku subagents, writing Obsidian notes and the enriched CSV. Usage - /process-articles 100 (default 50). Resumable - repeated invocations continue where the last one stopped.
---

# Process Articles

Process the next N pending articles (newest-first). N comes from the skill argument; default 50.

All commands run from the repo root. Requires `taxonomy/taxonomy.json` to exist (run `/build-taxonomy` first if missing).

## Steps

1. **Report starting state**: `python3 scripts/status.py`

2. **Fetch content** (best effort): `python3 scripts/fetch_content.py --limit N`
   Heavy failure rates are normal (paywalls, sandbox egress blocks). Failures route articles
   to the headline-only path automatically. If the environment has no network egress at all,
   note this in your final report but continue.

3. **Create batches**: `python3 scripts/make_batch.py --size 25 --count <ceil(N/25)>`
   The script prints one batch file path per line (or `NO_PENDING_ARTICLES`).

4. **Spawn one Haiku subagent per batch** (Agent tool, `model: "haiku"`, up to 4 in parallel).
   Each subagent prompt must contain:
   - The list of allowed keyword names from `taxonomy/taxonomy.json` (names only, comma-separated — read the file once and reuse the list).
   - The batch file path to Read.
   - This task contract (adapt the batch path):

   > Read the JSON batch file at <BATCH_PATH>. It contains news articles about innovation,
   > technology, and policy. For EACH article in the `articles` array, produce:
   > - `summary`: 1-2 sentences (max 350 chars) stating what the article reports.
   > - `takeaway`: 1 sentence (max 250 chars) — the "so what": the implication or key insight.
   > - `keywords`: 2-5 entries chosen ONLY from this allowed list (copy names exactly):
   >   <KEYWORD_LIST>. Include one region keyword (Canada / United States / Europe & UK /
   >   China / Global & Emerging Markets) when the geography is clear.
   > - `entities`: 0-4 proper nouns central to the article (companies, people, institutions).
   >
   > Articles with `content_basis: "full-text"` include the article text — ground your summary
   > in it. Articles with `content_basis: "headline-only"` have no text: infer cautiously from
   > headline, source, date, and your knowledge. NEVER fabricate specific figures, quotes, or
   > outcomes that the headline does not imply; describe what the article evidently covers.
   > For headline-only academic papers (sources like Research Policy, NBER, OECD), summarize
   > what the study examines rather than inventing findings.
   >
   > Write your output with the Write tool to <RESULT_PATH> as a raw JSON array (no markdown
   > fences, no commentary):
   > `[{"id": "...", "summary": "...", "takeaway": "...", "keywords": ["..."], "entities": ["..."]}]`
   > Include every article id from the batch exactly once. Then reply with just "done".

   RESULT_PATH = the batch path with `batch_` replaced by `result_`
   (e.g. `data/batches/result_20260612_193000_1.json`).

5. **Ingest each result**: `python3 scripts/ingest_results.py <result_path> <batch_path>`
   Parse the printed JSON summary.

6. **Retry rejected articles once**: collect all rejected IDs across batches, run
   `python3 scripts/make_batch.py --ids <id1> <id2> ...`, and spawn one more Haiku subagent
   for the retry batch — include the rejection reasons in the prompt so it can correct them
   (most common: a keyword not on the allowed list). Ingest the retry result.
   For IDs that fail a second time, append a `needs_review` ledger line for each:
   `python3 -c "import sys; sys.path.insert(0,'scripts'); import common,time,json; common.append_jsonl(common.LEDGER_PATH, [{'id': i, 'status': 'needs_review', 'reason': 'failed validation twice', 'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} for i in ['<id1>','<id2>']])"`

7. **Export + final report**: `python3 scripts/export_csv.py`, `python3 scripts/render_graph.py`
   (regenerates the interactive `output/graph.html`), then `python3 scripts/status.py`.
   Tell the user: how many processed this run, accepted/rejected/needs_review counts,
   full-text vs headline-only split, top keywords, and how many articles remain pending.

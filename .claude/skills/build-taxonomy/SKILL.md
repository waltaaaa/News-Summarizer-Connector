---
name: build-taxonomy
description: Build or rebuild the controlled keyword taxonomy (50-100 keywords) from a stratified sample of the article corpus. Produces taxonomy/taxonomy_proposed.md for user review, then freezes taxonomy/taxonomy.json. Run before /process-articles.
---

# Build Taxonomy

Goal: a controlled vocabulary of 50-100 concise keywords that every article will be tagged
from. Consistency matters more than coverage — fewer, sharper keywords beat many overlapping
ones, because the keywords are the hubs of the Obsidian graph and the future bridge to the
insight-articles list.

## Steps

1. Ensure `data/articles.jsonl` exists: `python3 scripts/extract_articles.py` (if missing).

2. Sample the corpus: `python3 scripts/sample_corpus.py` → `data/taxonomy_sample.jsonl`
   (400 headlines, stratified by source and year, seeded/reproducible).

3. Read the sample and propose 50-100 keywords organized in thematic groups
   (e.g. Regions / AI & Digital / Startups & Capital / Innovation Policy / Energy & Climate /
   Sectors / Trade & Geopolitics / Society). For each keyword: a short Title Case name,
   a one-line definition, and aliases (semicolon-separated) that catch likely near-miss
   phrasings. Region keywords (Canada, United States, Europe & UK, China, Global & Emerging
   Markets) should be included so the graph can cluster by geography.

4. Write the proposal to `taxonomy/taxonomy_proposed.md` as markdown tables with columns:
   `| Keyword | Definition | Aliases | Example headlines | Keep? |` (Keep? defaults to yes).

5. Ask the user to review/edit the table (rename, drop rows by setting Keep? to `no`, add
   rows). When they're satisfied: `python3 scripts/finalize_taxonomy.py` → `taxonomy/taxonomy.json`.

6. **Re-tagging warning**: if articles were already processed under an older taxonomy version,
   tell the user those notes keep their old tags (each ledger entry records its
   `taxonomy_version`); re-tagging requires clearing those ledger entries and re-running
   /process-articles for them.

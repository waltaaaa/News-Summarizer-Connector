"""Validate a Haiku subagent result file against its batch, append accepted
records to the ledger, and write Obsidian notes + keyword hub notes.

Usage: ingest_results.py <result.json> <batch.json>
Prints a JSON summary: {"accepted": N, "rejected": [{"id","reason"}], "skipped": N}
"""
import json
import os
import re
import sys
import time

import common

MAX_SUMMARY = 400
MAX_TAKEAWAY = 300


def parse_result_file(path):
    with open(path, encoding="utf-8") as f:
        raw = f.read().strip()
    # Tolerate markdown code fences
    fence = re.match(r"^```(?:json)?\s*(.*?)\s*```$", raw, re.S)
    if fence:
        raw = fence.group(1)
    return json.loads(raw)


def sanitize_filename(text, limit=60):
    text = re.sub(r'[<>:"/\\|?*\[\]#^]', "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit].strip()


def yaml_str(s):
    s = str(s).replace('"', "'")
    return f'"{s}"'


def note_filename(article):
    date = article.get("date") or "undated"
    head = sanitize_filename(article["headline"]) or "untitled"
    return f"{date} {head} ({article['id']}).md"


def write_article_note(article, rec):
    os.makedirs(common.VAULT_NEWS_DIR, exist_ok=True)
    kw_yaml = ", ".join(yaml_str(k) for k in rec["keywords"])
    ent_yaml = ", ".join(yaml_str(e) for e in rec.get("entities", []))
    wikilinks = " · ".join(f"[[{k}]]" for k in rec["keywords"])
    body = f"""---
id: {article['id']}
type: news-article
headline: {yaml_str(article['headline'])}
source: {yaml_str(article['source'])}
url: {yaml_str(article['url'])}
date: {article.get('date') or ''}
content_basis: {rec['content_basis']}
keywords: [{kw_yaml}]
entities: [{ent_yaml}]
---

## Summary

{rec['summary']}

## Key Takeaway

{rec['takeaway']}

## Keywords

{wikilinks}
"""
    path = os.path.join(common.VAULT_NEWS_DIR, note_filename(article))
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)
    return os.path.relpath(path, common.REPO_ROOT)


def ensure_hub_notes(keywords, taxonomy):
    os.makedirs(common.VAULT_KEYWORDS_DIR, exist_ok=True)
    defs = {k["name"]: k.get("definition", "") for k in taxonomy["keywords"]}
    for kw in keywords:
        path = os.path.join(common.VAULT_KEYWORDS_DIR, f"{sanitize_filename(kw, 80)}.md")
        if os.path.exists(path):
            continue
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"""---
type: keyword
---

# {kw}

{defs.get(kw, '')}

Articles tagged with this keyword appear as backlinks (and in the graph view).
""")


def validate_item(item, batch_articles, lookup):
    if not isinstance(item, dict) or "id" not in item:
        return None, "item is not an object with an id"
    aid = item["id"]
    if aid not in batch_articles:
        return None, f"id {aid} not in batch"
    summary = str(item.get("summary", "")).strip()
    takeaway = str(item.get("takeaway", "")).strip()
    if not summary:
        return None, "empty summary"
    if not takeaway:
        return None, "empty takeaway"
    if len(summary) > MAX_SUMMARY:
        return None, f"summary too long ({len(summary)} chars)"
    if len(takeaway) > MAX_TAKEAWAY:
        return None, f"takeaway too long ({len(takeaway)} chars)"
    raw_keywords = item.get("keywords", [])
    if not isinstance(raw_keywords, list) or not (1 <= len(raw_keywords) <= 5):
        return None, "keywords must be a list of 1-5 entries"
    keywords = []
    for k in raw_keywords:
        canonical = lookup.get(str(k).strip().lower())
        if not canonical:
            return None, f"unknown keyword: '{k}'"
        if canonical not in keywords:
            keywords.append(canonical)
    entities = [str(e).strip() for e in item.get("entities", [])
                if str(e).strip()][:4] if isinstance(item.get("entities"), list) else []
    return {"summary": summary, "takeaway": takeaway,
            "keywords": keywords, "entities": entities}, None


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: ingest_results.py <result.json> <batch.json>")
    result_path, batch_path = sys.argv[1], sys.argv[2]

    with open(batch_path, encoding="utf-8") as f:
        batch = json.load(f)
    batch_articles = {a["id"]: a for a in batch["articles"]}
    articles_full = {a["id"]: a for a in common.load_articles()}
    taxonomy = common.load_taxonomy()
    lookup = common.taxonomy_lookup(taxonomy)
    ledger = common.load_ledger()

    try:
        items = parse_result_file(result_path)
        if not isinstance(items, list):
            raise ValueError("top-level JSON is not an array")
    except (json.JSONDecodeError, ValueError) as e:
        print(json.dumps({"accepted": 0, "skipped": 0, "rejected": [
            {"id": aid, "reason": f"result file unparseable: {e}"}
            for aid in batch_articles]}))
        return

    accepted, rejected, skipped = [], [], 0
    seen_ids = set()
    for item in items:
        rec, err = validate_item(item, batch_articles, lookup)
        if err:
            rejected.append({"id": item.get("id", "?") if isinstance(item, dict) else "?",
                             "reason": err})
            continue
        aid = item["id"]
        if aid in seen_ids:
            continue
        seen_ids.add(aid)
        if aid in ledger and ledger[aid].get("status") == "done":
            skipped += 1
            continue
        article = articles_full[aid]
        rec["content_basis"] = batch_articles[aid].get("content_basis", "headline-only")
        ensure_hub_notes(rec["keywords"], taxonomy)
        note_path = write_article_note(article, rec)
        ledger_rec = {"id": aid, "summary": rec["summary"], "takeaway": rec["takeaway"],
                      "keywords": rec["keywords"], "entities": rec["entities"],
                      "content_basis": rec["content_basis"], "status": "done",
                      "note": note_path, "batch": batch["batch_id"],
                      "taxonomy_version": taxonomy["version"],
                      "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        common.append_jsonl(common.LEDGER_PATH, [ledger_rec])
        accepted.append(aid)

    # Articles in the batch that got no valid item at all
    missing = set(batch_articles) - seen_ids - {r["id"] for r in rejected} - set(ledger)
    for aid in sorted(missing):
        rejected.append({"id": aid, "reason": "no result returned for this id"})

    print(json.dumps({"accepted": len(accepted), "skipped": skipped, "rejected": rejected}))


if __name__ == "__main__":
    main()

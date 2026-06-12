"""Regenerate output/articles_enriched.csv from articles.jsonl + ledger.jsonl."""
import csv
import os

import common


def main():
    os.makedirs(os.path.dirname(common.CSV_PATH), exist_ok=True)
    ledger = common.load_ledger()
    articles = common.load_articles()

    with open(common.CSV_PATH, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["id", "headline", "source", "url", "date", "notes",
                    "summary", "key_takeaway", "keywords", "entities",
                    "content_basis", "status", "note_path"])
        filled = 0
        for a in articles:
            rec = ledger.get(a["id"], {})
            if rec:
                filled += 1
            w.writerow([
                a["id"], a["headline"], a["source"], a["url"], a["date"], a["notes"],
                rec.get("summary", ""), rec.get("takeaway", ""),
                "; ".join(rec.get("keywords", [])), "; ".join(rec.get("entities", [])),
                rec.get("content_basis", ""), rec.get("status", ""),
                rec.get("note", ""),
            ])
    print(f"wrote {common.CSV_PATH}: {len(articles)} rows, {filled} enriched")


if __name__ == "__main__":
    main()

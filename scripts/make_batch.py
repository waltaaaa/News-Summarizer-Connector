"""Create batch input files of pending articles for Haiku subagents.

Pending = articles.jsonl minus ledger.jsonl minus IDs already sitting in an
unconsumed batch file. Newest-first. Attaches cached full text when available.
"""
import argparse
import glob
import json
import os
import time
import uuid

import common

MAX_TEXT_CHARS = 3500


def ids_in_open_batches():
    """IDs in batch files that don't yet have a matching result file."""
    taken = set()
    for bf in glob.glob(os.path.join(common.BATCH_DIR, "batch_*.json")):
        result = bf.replace("batch_", "result_", 1)
        if os.path.exists(result):
            continue
        try:
            with open(bf, encoding="utf-8") as f:
                batch = json.load(f)
            taken.update(a["id"] for a in batch["articles"])
        except (json.JSONDecodeError, KeyError):
            continue
    return taken


def content_for(aid):
    path = os.path.join(common.CACHE_DIR, f"{aid}.json")
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                cached = json.load(f)
            if cached.get("status") == "ok" and cached.get("text"):
                return "full-text", cached["text"][:MAX_TEXT_CHARS]
        except json.JSONDecodeError:
            pass
    return "headline-only", None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", type=int, default=25)
    ap.add_argument("--count", type=int, default=1)
    ap.add_argument("--ids", nargs="*", help="build a single batch from specific IDs (retry)")
    args = ap.parse_args()

    os.makedirs(common.BATCH_DIR, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:4]

    if args.ids:
        articles = {a["id"]: a for a in common.load_articles()}
        pool = [articles[i] for i in args.ids if i in articles]
        chunks = [pool] if pool else []
    else:
        taken = ids_in_open_batches()
        pool = [a for a in common.pending_articles() if a["id"] not in taken]
        pool = pool[: args.size * args.count]
        chunks = [pool[i:i + args.size] for i in range(0, len(pool), args.size)]

    paths = []
    for k, chunk in enumerate(chunks, 1):
        batch_id = f"{stamp}_{k}"
        items = []
        for a in chunk:
            basis, text = content_for(a["id"])
            items.append({"id": a["id"], "headline": a["headline"], "source": a["source"],
                          "date": a["date"], "notes": a["notes"],
                          "content_basis": basis, "text": text})
        path = os.path.join(common.BATCH_DIR, f"batch_{batch_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"batch_id": batch_id, "articles": items}, f, ensure_ascii=False, indent=1)
        paths.append(path)
        print(path)

    if not paths:
        print("NO_PENDING_ARTICLES")


if __name__ == "__main__":
    main()

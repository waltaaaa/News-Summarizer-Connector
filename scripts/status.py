"""Pipeline status: processed / pending / needs_review counts + cache stats."""
import glob
import json
import os
from collections import Counter

import common


def main():
    articles = common.load_articles()
    ledger = common.load_ledger()
    statuses = Counter(r.get("status", "?") for r in ledger.values())
    done = statuses.get("done", 0)
    pending = len(articles) - len(ledger)

    cache_status = Counter()
    for path in glob.glob(os.path.join(common.CACHE_DIR, "*.json")):
        try:
            with open(path, encoding="utf-8") as f:
                cache_status[json.load(f).get("status", "?")] += 1
        except (json.JSONDecodeError, OSError):
            cache_status["corrupt"] += 1

    basis = Counter(r.get("content_basis", "?") for r in ledger.values()
                    if r.get("status") == "done")
    kw = Counter()
    for r in ledger.values():
        if r.get("status") == "done":
            kw.update(r.get("keywords", []))

    print(f"articles total:   {len(articles)}")
    print(f"processed (done): {done}")
    print(f"needs_review:     {statuses.get('needs_review', 0)}")
    print(f"pending:          {pending}")
    print(f"fetch cache:      {dict(cache_status) or 'empty'}")
    print(f"content basis:    {dict(basis) or '-'}")
    if kw:
        print("top keywords:")
        for k, c in kw.most_common(15):
            print(f"  {c:4d}  {k}")


if __name__ == "__main__":
    main()

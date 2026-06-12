"""Stratified sample of headlines for taxonomy building.

Strata: top-20 sources sampled proportionally + a long-tail bucket, crossed
with year. Seeded RNG so the sample is reproducible.
"""
import argparse
import json
import random
from collections import Counter, defaultdict

import common


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", type=int, default=400)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default=common.REPO_ROOT + "/data/taxonomy_sample.jsonl")
    args = ap.parse_args()

    articles = common.load_articles()
    rng = random.Random(args.seed)

    top_sources = {s for s, _ in Counter(a["source"] for a in articles).most_common(20)}
    strata = defaultdict(list)
    for a in articles:
        src = a["source"] if a["source"] in top_sources else "_longtail"
        year = (a.get("date") or "0000")[:4]
        strata[(src, year)].append(a)

    total = len(articles)
    sample = []
    for key, group in sorted(strata.items()):
        k = max(1, round(len(group) / total * args.size))
        sample.extend(rng.sample(group, min(k, len(group))))

    rng.shuffle(sample)
    sample = sample[:args.size]
    with open(args.out, "w", encoding="utf-8") as f:
        for a in sample:
            f.write(json.dumps({"id": a["id"], "headline": a["headline"],
                                "source": a["source"], "date": a["date"]},
                               ensure_ascii=False) + "\n")
    print(f"wrote {len(sample)} sampled headlines to {args.out}")


if __name__ == "__main__":
    main()

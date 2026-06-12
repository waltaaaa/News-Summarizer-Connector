"""Parse taxonomy/taxonomy_proposed.md (markdown table) into taxonomy/taxonomy.json.

Rows whose Keep? column is 'no' (case-insensitive) are dropped.
Table columns: | Keyword | Definition | Aliases | Example headlines | Keep? |
"""
import json
import os
import re
import sys
from datetime import date

import common

PROPOSED = os.path.join(common.REPO_ROOT, "taxonomy", "taxonomy_proposed.md")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else PROPOSED
    keywords = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) < 2 or cells[0].lower() in ("keyword", "") or set(cells[0]) <= {"-", " ", ":"}:
                continue
            keep = cells[4].lower() if len(cells) > 4 else "yes"
            if keep.startswith("n"):
                continue
            name = cells[0]
            definition = cells[1] if len(cells) > 1 else ""
            aliases = [a.strip() for a in re.split(r"[;,]", cells[2]) if a.strip()] \
                if len(cells) > 2 and cells[2] else []
            keywords.append({"name": name, "definition": definition, "aliases": aliases})

    # Reject duplicate canonical names
    names = [k["name"].lower() for k in keywords]
    dupes = {n for n in names if names.count(n) > 1}
    if dupes:
        sys.exit(f"ERROR: duplicate keywords in table: {dupes}")

    out = {"version": 1, "frozen": date.today().isoformat(), "keywords": keywords}
    with open(common.TAXONOMY_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"wrote {len(keywords)} keywords to {common.TAXONOMY_PATH}")


if __name__ == "__main__":
    main()

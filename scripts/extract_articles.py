"""Parse the source xlsx into data/articles.jsonl (stdlib only)."""
import argparse
import json
import re
import sys
import zipfile
from xml.etree import ElementTree as ET

import common

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
T_TAG = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t"


def parse_xlsx(path):
    z = zipfile.ZipFile(path)
    ss_root = ET.fromstring(z.read("xl/sharedStrings.xml"))
    shared = ["".join(t.text or "" for t in si.iter(T_TAG)) for si in ss_root.findall("m:si", NS)]
    sheet = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))

    def cellval(c):
        v = c.find("m:v", NS)
        if v is None:
            return ""
        return shared[int(v.text)] if c.get("t") == "s" else (v.text or "")

    rows = []
    for row in sheet.findall(".//m:row", NS):
        cells = {}
        for c in row.findall("m:c", NS):
            col = re.match(r"[A-Z]+", c.get("r")).group()
            cells[col] = cellval(c)
        rows.append((int(row.get("r")), cells))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--xlsx", default=common.XLSX_PATH)
    ap.add_argument("--out", default=common.ARTICLES_PATH)
    args = ap.parse_args()

    rows = parse_xlsx(args.xlsx)
    records = []
    for rownum, cells in rows:
        if rownum == 1:  # header
            continue
        headline = cells.get("A", "").strip()
        source = cells.get("B", "").strip()
        url = cells.get("C", "").strip()
        if not headline and not url:
            continue
        records.append({
            "id": common.article_id(url, headline, source),
            "row": rownum,
            "headline": headline,
            "source": source,
            "url": url,
            "url_normalized": common.normalize_url(url) if url else "",
            "date": common.excel_date_to_iso(cells.get("D", "")),
            "notes": cells.get("E", "").strip(),
        })

    records.sort(key=lambda r: r["row"])
    # Dedupe on ID (same article logged twice w/ different tracking params): keep first.
    seen, unique, dropped = set(), [], 0
    for r in records:
        if r["id"] in seen:
            dropped += 1
            print(f"  dropped duplicate: {r['id']} row {r['row']} {r['headline'][:60]}",
                  file=sys.stderr)
            continue
        seen.add(r["id"])
        unique.append(r)
    with open(args.out, "w", encoding="utf-8") as f:
        for r in unique:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(unique)} unique articles to {args.out} ({dropped} duplicates dropped)")


if __name__ == "__main__":
    main()

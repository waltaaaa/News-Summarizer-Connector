"""Shared utilities: article IDs, URL normalization, Excel date conversion, paths."""
import hashlib
import json
import os
import re
from datetime import date, timedelta
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XLSX_PATH = os.path.join(REPO_ROOT, "data", "source", "News_Repository__InnoTech.xlsx")
ARTICLES_PATH = os.path.join(REPO_ROOT, "data", "articles.jsonl")
LEDGER_PATH = os.path.join(REPO_ROOT, "data", "ledger.jsonl")
CACHE_DIR = os.path.join(REPO_ROOT, "data", "cache")
BATCH_DIR = os.path.join(REPO_ROOT, "data", "batches")
TAXONOMY_PATH = os.path.join(REPO_ROOT, "taxonomy", "taxonomy.json")
VAULT_NEWS_DIR = os.path.join(REPO_ROOT, "vault", "articles", "news")
VAULT_KEYWORDS_DIR = os.path.join(REPO_ROOT, "vault", "keywords")
CSV_PATH = os.path.join(REPO_ROOT, "output", "articles_enriched.csv")

TRACKING_PARAMS = re.compile(
    r"^(utm_\w+|fbclid|gclid|mc_cid|mc_eid|ref|source|cmpid|smid|ocid|igshid)$", re.I
)


def normalize_url(url: str) -> str:
    url = url.strip()
    parts = urlsplit(url)
    scheme = (parts.scheme or "https").lower()
    host = parts.netloc.lower()
    path = parts.path.rstrip("/")
    query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
             if not TRACKING_PARAMS.match(k)]
    query.sort()
    return urlunsplit((scheme, host, path, urlencode(query), ""))


def article_id(url: str, headline: str = "", source: str = "", prefix: str = "n") -> str:
    basis = normalize_url(url) if url and url.strip() else f"{headline}|{source}"
    return f"{prefix}-" + hashlib.sha1(basis.encode("utf-8")).hexdigest()[:12]


def excel_date_to_iso(serial) -> str:
    try:
        return (date(1899, 12, 30) + timedelta(days=int(float(serial)))).isoformat()
    except (ValueError, TypeError):
        return ""


def read_jsonl(path):
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def append_jsonl(path, records):
    with open(path, "a", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def load_articles():
    return read_jsonl(ARTICLES_PATH)


def load_ledger():
    """Ledger as {id: latest record} (last-write-wins)."""
    result = {}
    for rec in read_jsonl(LEDGER_PATH):
        result[rec["id"]] = rec
    return result


def load_taxonomy():
    with open(TAXONOMY_PATH, encoding="utf-8") as f:
        return json.load(f)


def taxonomy_lookup(taxonomy):
    """Case-insensitive map of name/alias -> canonical keyword name."""
    lookup = {}
    for kw in taxonomy["keywords"]:
        lookup[kw["name"].lower()] = kw["name"]
        for alias in kw.get("aliases", []):
            lookup[alias.lower()] = kw["name"]
    return lookup


def pending_articles():
    """Articles not yet in ledger, newest-first by date then row."""
    done = set(load_ledger().keys())
    pend = [a for a in load_articles() if a["id"] not in done]
    pend.sort(key=lambda a: (a.get("date") or "", -a.get("row", 0)), reverse=True)
    return pend

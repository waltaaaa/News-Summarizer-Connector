"""Fetch article URLs and cache extracted text. Failure is a normal outcome
(paywall, 403, timeout, egress block) and routes the article to the
headline-only summarization path."""
import argparse
import gzip
import json
import os
import re
import socket
import time
import urllib.request
import urllib.error
from html.parser import HTMLParser

import common

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
SKIP_TAGS = {"script", "style", "noscript", "nav", "header", "footer", "form",
             "svg", "aside", "iframe"}
PAYWALL_MARKERS = [
    "subscribe to continue", "subscribe to read", "sign in to read",
    "create a free account", "this content is for subscribers",
    "to continue reading", "already a subscriber",
]
MAX_CHARS = 8000
THIN_THRESHOLD = 800


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in SKIP_TAGS:
            self.skip_depth += 1

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS and self.skip_depth > 0:
            self.skip_depth -= 1

    def handle_data(self, data):
        if self.skip_depth == 0:
            text = data.strip()
            if text:
                self.parts.append(text)


def html_to_text(html: str) -> str:
    p = TextExtractor()
    try:
        p.feed(html)
    except Exception:
        pass
    text = "\n".join(p.parts)
    return re.sub(r"\n{3,}", "\n\n", text)


def fetch_one(url: str, timeout: int):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read(2_000_000)
            if resp.headers.get("Content-Encoding") == "gzip":
                try:
                    raw = gzip.decompress(raw)
                except OSError:
                    pass
            charset = resp.headers.get_content_charset() or "utf-8"
            html = raw.decode(charset, errors="replace")
            text = html_to_text(html)[:MAX_CHARS]
            lower = text.lower()
            if len(text) < THIN_THRESHOLD or any(m in lower for m in PAYWALL_MARKERS):
                return {"status": "thin", "http_code": resp.status, "text": text}
            return {"status": "ok", "http_code": resp.status, "text": text}
    except urllib.error.HTTPError as e:
        return {"status": "error", "http_code": e.code, "text": "", "error": f"HTTP {e.code}"}
    except (urllib.error.URLError, socket.timeout, ConnectionError, OSError,
            ValueError, Exception) as e:
        return {"status": "error", "http_code": None, "text": "",
                "error": f"{type(e).__name__}: {e}"[:200]}


def cache_path(aid):
    return os.path.join(common.CACHE_DIR, f"{aid}.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=50,
                    help="fetch at most N pending-and-uncached articles")
    ap.add_argument("--ids", nargs="*", help="fetch specific article IDs (refetch)")
    ap.add_argument("--timeout", type=int, default=15)
    args = ap.parse_args()

    os.makedirs(common.CACHE_DIR, exist_ok=True)
    articles = {a["id"]: a for a in common.load_articles()}

    if args.ids:
        targets = [articles[i] for i in args.ids if i in articles]
    else:
        targets = [a for a in common.pending_articles()
                   if not os.path.exists(cache_path(a["id"]))][:args.limit]

    counts = {"ok": 0, "thin": 0, "error": 0}
    for i, art in enumerate(targets, 1):
        result = fetch_one(art["url"], args.timeout)
        result.update({"id": art["id"], "chars": len(result["text"]),
                       "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        with open(cache_path(art["id"]), "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False)
        counts[result["status"]] += 1
        print(f"[{i}/{len(targets)}] {result['status']:5s} {art['id']} {art['url'][:70]}")

    print(f"\nfetched {len(targets)}: {counts}")


if __name__ == "__main__":
    main()

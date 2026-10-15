#!/usr/bin/env python3
"""Dump a MediaWiki wiki (built for peak.wiki.gg): current page text + media files.

Text  : list=allpages enumerates titles per namespace (real continue tokens, nothing missed),
        then prop=revisions fetches wikitext 50 titles per request.
Media : list=allimages -> download with bounded concurrency, unique cache-buster and sha1 check.

Politeness: one request at a time with a delay, 429 -> honour retry-after, 5xx -> back off.
"""

import argparse
import hashlib
import json
import os
import queue
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from xml.sax.saxutils import escape

UA_DEFAULT = "peak-wiki-dump/1.0 (+https://walruslab.org; contact: attacca@walruslab.org)"

# Cloudflare fronts peak.wiki.gg and caches a RECOMPRESSED image rendition under the URL the API
# hands out. A cached URL returns that optimised file (bytes/sha1 != the upload); a cache MISS
# goes to the origin and returns the uploaded original. So every media URL gets a unique
# cache-buster, and the sha1 from the API is verified (with a re-bust on mismatch).
CACHE_BUST_MEDIA = True

NS_NAMES = {
    0: "main", 1: "talk", 2: "user", 3: "user-talk", 4: "project", 5: "project-talk",
    6: "file", 7: "file-talk", 8: "mediawiki", 9: "mediawiki-talk", 10: "template",
    11: "template-talk", 12: "help", 13: "help-talk", 14: "category", 15: "category-talk",
    828: "module", 829: "module-talk",
}
DEFAULT_NS = [0, 4, 10, 14, 828, 2, 1, 3, 5, 6, 7, 8, 9, 11, 12, 13, 829]


def log(*a):
    print(*a, file=sys.stderr, flush=True)


class Api:
    def __init__(self, api_url, ua, delay=1.0, max_retry=6):
        self.api = api_url
        self.ua = ua
        self.delay = delay
        self.max_retry = max_retry
        self._last = 0.0
        self._lock = threading.Lock()
        self.requests = 0
        self.throttled = 0

    def _wait(self):
        with self._lock:
            gap = self.delay - (time.time() - self._last)
            if gap > 0:
                time.sleep(gap)
            self._last = time.time()

    def raw(self, **params):
        params.setdefault("format", "json")
        params.setdefault("formatversion", "2")
        url = self.api + "?" + urllib.parse.urlencode(params)
        for attempt in range(self.max_retry):
            self._wait()
            req = urllib.request.Request(url, headers={"User-Agent": self.ua})
            try:
                with urllib.request.urlopen(req, timeout=120) as resp:
                    body = resp.read()
                self.requests += 1
                return body.decode("utf-8", "replace")
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    self.throttled += 1
                    wait = int(e.headers.get("retry-after") or 30) + 1
                    log(f"  429 rate-limited, sleeping {wait}s")
                    time.sleep(wait)
                    continue
                if 500 <= e.code < 600:
                    time.sleep(5 * (attempt + 1))
                    continue
                raise
            except Exception as e:  # noqa: BLE001 - transient network
                log(f"  retry after {e!r}")
                time.sleep(3 * (attempt + 1))
        raise RuntimeError(f"giving up on {url}")

    def json(self, **params):
        return json.loads(self.raw(**params))


def list_titles(api, ns):
    """Every page title in one namespace, via list=allpages continuation."""
    titles, cont = [], {}
    while True:
        d = api.json(action="query", list="allpages", aplimit="500",
                     apnamespace=str(ns), **cont)
        titles += [p["title"] for p in d["query"]["allpages"]]
        if "continue" in d:
            cont = d["continue"]
        else:
            return titles


def fetch_texts(api, titles, batch=50):
    """Yield {ns,title,pageid,revid,timestamp,text} with the current revision of each title."""
    for i in range(0, len(titles), batch):
        chunk = titles[i:i + batch]
        d = api.json(action="query", prop="revisions", rvprop="content|ids|timestamp",
                     rvslots="main", titles="|".join(chunk))
        for pg in d["query"]["pages"]:
            rev = (pg.get("revisions") or [{}])[0]
            slots = rev.get("slots", {}).get("main", {})
            yield {
                "ns": pg.get("ns"), "title": pg.get("title"), "pageid": pg.get("pageid"),
                "revid": rev.get("revid"), "timestamp": rev.get("timestamp"),
                "text": slots.get("content", ""),
            }


def dump_text(api, outdir, namespaces, delay_between_ns=1.0):
    os.makedirs(outdir, exist_ok=True)
    jsonl_path = os.path.join(outdir, "pages.jsonl")
    stats = []
    with open(jsonl_path, "w", encoding="utf-8") as jf:
        for ns in namespaces:
            name = NS_NAMES.get(ns, f"ns{ns}")
            xml_path = os.path.join(outdir, f"text-{ns}-{name}.xml")
            titles = list_titles(api, ns)
            n_pages = n_bytes = 0
            with open(xml_path, "w", encoding="utf-8") as xf:
                xf.write('<?xml version="1.0" encoding="UTF-8"?>\n<dump>\n')
                for rec in fetch_texts(api, titles):
                    jf.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    xf.write("  <page>\n"
                             f"    <title>{escape(rec['title'])}</title>\n"
                             f"    <ns>{rec['ns']}</ns>\n"
                             f"    <id>{rec['pageid']}</id>\n"
                             f"    <revision><id>{rec['revid']}</id>"
                             f"<timestamp>{rec['timestamp']}</timestamp>"
                             f"<text>{escape(rec['text'])}</text></revision>\n"
                             "  </page>\n")
                    n_pages += 1
                    n_bytes += len(rec["text"].encode())
                xf.write("</dump>\n")
            stats.append((ns, name, n_pages, n_bytes))
            log(f"ns{ns} {name}: {n_pages} pages, {n_bytes} B wikitext -> {xml_path}")
            time.sleep(delay_between_ns)
    return stats, jsonl_path


def list_media(api):
    items, cont = [], {}
    while True:
        d = api.json(action="query", list="allimages", ailimit="500",
                     aiprop="url|size|mime|sha1", **cont)
        items += d["query"]["allimages"]
        if "continue" in d:
            cont = d["continue"]
        else:
            return items


def dump_media(api, outdir, items, concurrency=4, limit=None, resume=True):
    imgdir = os.path.join(outdir, "images")
    os.makedirs(imgdir, exist_ok=True)
    todo = items[:limit] if limit else items
    q = queue.Queue()
    for it in todo:
        q.put(it)
    results, lock = [], threading.Lock()
    t0 = time.time()

    def worker():
        while True:
            try:
                it = q.get_nowait()
            except queue.Empty:
                return
            name = urllib.parse.unquote(it["name"])
            path = os.path.join(imgdir, name.replace("/", "_"))
            base = it["url"].split("?", 1)[0]
            rec = {"name": it["name"], "api_url": it["url"], "mime": it.get("mime"),
                   "api_size": it.get("size"), "api_sha1": it.get("sha1"), "path": path}
            if resume and os.path.exists(path) and it.get("size") \
                    and os.path.getsize(path) == it["size"]:
                rec.update(status="cached", bytes=it["size"], sha1_ok=True)
                with lock:
                    results.append(rec)
                continue
            for attempt in range(api.max_retry):
                if CACHE_BUST_MEDIA:
                    b = hashlib.sha1(f"{it['name']}|{attempt}|{time.time()}".encode()).hexdigest()[:16]
                    url = f"{base}?d={b}"
                else:
                    url = it["url"]
                rec["url_used"] = url
                try:
                    with urllib.request.urlopen(
                            urllib.request.Request(url, headers={"User-Agent": api.ua}),
                            timeout=180) as resp:
                        data = resp.read()
                except urllib.error.HTTPError as e:
                    if e.code == 429:
                        time.sleep(int(e.headers.get("retry-after") or 30) + 1)
                        continue
                    rec.update(status=f"http-{e.code}")
                    break
                except Exception as e:  # noqa: BLE001
                    rec.update(status=f"error: {e}")
                    time.sleep(2 * (attempt + 1))
                    continue
                digest = hashlib.sha1(data).hexdigest()
                if it.get("sha1") and digest != it["sha1"]:
                    # recompressed CDN rendition got cached under this key - bust again
                    log(f"  {it['name']}: recompressed bytes (sha1 {digest[:8]}), re-busting")
                    rec.update(status="sha1-retry")
                    continue
                with open(path, "wb") as f:
                    f.write(data)
                rec.update(status="ok", bytes=len(data), got_sha1=digest,
                           sha1_ok=(digest == it["sha1"]) if it.get("sha1") else None)
                break
            with lock:
                results.append(rec)
                done = len(results)
            if done % 100 == 0:
                log(f"  media {done}/{len(todo)}")

    threads = [threading.Thread(target=worker) for _ in range(concurrency)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    el = time.time() - t0
    tot = sum(r.get("bytes") or 0 for r in results)
    manifest = os.path.join(outdir, "media-manifest.jsonl")
    with open(manifest, "w", encoding="utf-8") as f:
        for r in sorted(results, key=lambda r: r["name"]):
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    bad = [r for r in results if r.get("sha1_ok") is False]
    log(f"media: {len(results)} files, {tot/1e6:.1f} MB in {el:.0f}s "
        f"({tot/1e6/max(el,1e-9):.2f} MB/s), sha1 mismatches: {len(bad)}")
    return results, manifest, el


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--api", default="https://peak.wiki.gg/api.php")
    ap.add_argument("--out", default="peak-dump")
    ap.add_argument("--namespaces", default=",".join(map(str, DEFAULT_NS)))
    ap.add_argument("--skip-text", action="store_true")
    ap.add_argument("--skip-media", action="store_true")
    ap.add_argument("--media-limit", type=int, default=None)
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--delay", type=float, default=1.0)
    ap.add_argument("--user-agent", default=UA_DEFAULT)
    args = ap.parse_args()

    api = Api(args.api, args.user_agent, delay=args.delay)
    ns = [int(x) for x in args.namespaces.split(",") if x.strip() != ""]
    summary = {"api": args.api, "started": time.time()}

    if not args.skip_text:
        t0 = time.time()
        stats, jsonl = dump_text(api, args.out, ns)
        summary["text"] = {
            "seconds": round(time.time() - t0, 1),
            "pages": sum(s[2] for s in stats),
            "wikitext_bytes": sum(s[3] for s in stats),
            "jsonl": jsonl,
            "per_namespace": [{"ns": s[0], "name": s[1], "pages": s[2], "bytes": s[3]}
                              for s in stats],
        }
    if not args.skip_media:
        items = list_media(api)
        summary["media_total_on_wiki"] = {"files": len(items),
                                          "bytes": sum(i.get("size", 0) for i in items)}
        res, manifest, el = dump_media(api, args.out, items, args.concurrency, args.media_limit)
        summary["media"] = {"seconds": round(el, 1), "files": len(res),
                            "bytes": sum(r.get("bytes") or 0 for r in res), "manifest": manifest,
                            "sha1_mismatches": sum(1 for r in res if r.get("sha1_ok") is False)}
    summary["api_requests"] = api.requests
    summary["throttled_429"] = api.throttled
    summary["finished"] = time.time()
    with open(os.path.join(args.out, "dump-summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

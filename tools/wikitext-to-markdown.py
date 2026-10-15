#!/usr/bin/env python3
"""Turn a dumped MediaWiki wiki into Markdown.

For every content page it asks the API for the RENDERED HTML (action=parse, so templates,
infoboxes and tables are resolved), cleans the layout HTML away, rewrites image/link URLs to
point at the locally downloaded media and at sibling .md files, and runs pandoc (html -> gfm).

Layout produced under --out:
    pages/<Title>.md      one file per page, YAML front matter + Markdown
    INDEX.md              every page, linked
    <NAME>.md             every page concatenated (one big file)
Image links are written relative to the file that carries them.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

UA_DEFAULT = "peak-wiki-md/1.0 (+https://walruslab.org; contact: attacca@walruslab.org)"

# In-process HTML -> Markdown. Spawning pandoc per page costs a process (and, on this host,
# file descriptors) per page; markdownify does the same job inside the worker threads.
try:
    from markdownify import markdownify as _markdownify

    HAVE_MARKDOWNIFY = True
except ImportError:  # pragma: no cover
    _markdownify = None
    HAVE_MARKDOWNIFY = False


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def slug(title):
    s = title.replace("/", "_")
    s = re.sub(r'[<>:"\\|?*]', "_", s)
    return s.strip().strip(".") or "untitled"


WINDOWS_ILLEGAL = re.compile(r'[<>:"|?*]')


def sanitize_name(name):
    """A media filename that is legal on every OS - the wiki has files with '?' in the name."""
    return WINDOWS_ILLEGAL.sub("_", name).replace("/", "_")


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

    def json(self, **params):
        params.setdefault("format", "json")
        params.setdefault("formatversion", "2")
        url = self.api + "?" + urllib.parse.urlencode(params)
        for attempt in range(self.max_retry):
            self._wait()
            req = urllib.request.Request(url, headers={"User-Agent": self.ua})
            try:
                with urllib.request.urlopen(req, timeout=120) as resp:
                    body = resp.read().decode("utf-8", "replace")
                self.requests += 1
                return json.loads(body)
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
            except Exception as e:  # noqa: BLE001
                log(f"  retry after {e!r}")
                time.sleep(3 * (attempt + 1))
        raise RuntimeError(f"giving up on {url}")


def list_titles(api, ns, include_redirects=False):
    titles, cont = [], {}
    while True:
        p = dict(action="query", list="allpages", aplimit="500", apnamespace=str(ns), **cont)
        if not include_redirects:
            p["apfilterredir"] = "nonredirects"
        d = api.json(**p)
        titles += [x["title"] for x in d["query"]["allpages"]]
        if "continue" in d:
            cont = d["continue"]
        else:
            return titles


class Rewriter:
    """Rewrites /images/... and /wiki/... URLs inside the rendered HTML to local paths."""

    def __init__(self, base, image_dir, titles, img_prefix, page_prefix):
        self.base = base.rstrip("/")
        self.image_dir = image_dir
        self.img_prefix = img_prefix
        self.page_prefix = page_prefix
        self.titles = titles
        self.missing_images = set()
        self.rewritten_links = 0

    def _image_path(self, url):
        p = urllib.parse.unquote(url.split("?", 1)[0])
        if p.startswith("/images/thumb/"):
            parts = p.split("/")
            if len(parts) < 5:
                return None
            name = parts[3]
        elif p.startswith("/images/"):
            name = p[len("/images/"):]
        else:
            return None
        local = sanitize_name(name)
        if not os.path.exists(os.path.join(self.image_dir, local)):
            self.missing_images.add(name)
            return None
        return self.img_prefix + urllib.parse.quote(local)

    def _href(self, url):
        frag = ""
        if "#" in url:
            url, frag = url.split("#", 1)
            frag = "#" + frag
        title = None
        for prefix in (self.base + "/wiki/", "/wiki/"):
            if url.startswith(prefix):
                title = url[len(prefix):]
                break
        if title is None:
            for prefix in (self.base + "/index.php", "/index.php"):
                if url.startswith(prefix):
                    q = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
                    if "title" in q:
                        title = q["title"][0]
                    break
        if title is None:
            return None
        title = urllib.parse.unquote(title).replace("_", " ")
        if title in self.titles:
            self.rewritten_links += 1
            return self.page_prefix + urllib.parse.quote(slug(title)) + ".md" + frag
        return f"{self.base}/wiki/{urllib.parse.quote(title.replace(' ', '_'))}{frag}"

    def html(self, html, clean_layout=True):
        if clean_layout:
            html = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", "", html, flags=re.S | re.I)
            # layout-only markup: keep the content, drop the boxes
            html = re.sub(r"</?div\b[^>]*>", "\n", html, flags=re.I)
            html = re.sub(r"</?span\b[^>]*>", "", html, flags=re.I)
            html = re.sub(r"</?(o|u)l\b[^>]*>", "\n", html, flags=re.I)

        # "expanding it" / "[edit]" links point at the edit form, not at content
        html = re.sub(r'<a\b[^>]*href="[^"]*[?&]action=edit[^"]*"[^>]*>(.*?)</a>',
                      r"\1", html, flags=re.S | re.I)
        html = re.sub(r'<a\b[^>]*href="[^"]*[?&]redlink=1[^"]*"[^>]*>(.*?)</a>',
                      r"\1", html, flags=re.S | re.I)

        html = re.sub(r'(<img\b[^>]*?)src="(/images/[^"]*)"',
                      lambda m: (f'{m.group(1)}src="{self._image_path(m.group(2))}"'
                                 if self._image_path(m.group(2)) else m.group(0)), html)
        html = re.sub(r'(<a\b[^>]*?)href="((?:https?://peak\.wiki\.gg)?/(?:wiki|index\.php)[^"]*)"',
                      lambda m: (f'{m.group(1)}href="{self._href(m.group(2))}"'
                                 if self._href(m.group(2)) else m.group(0)), html)

        # Any attribute pandoc cannot carry into Markdown makes it fall back to raw HTML for the
        # whole element, so strip everything except the ones that carry meaning.
        html = re.sub(r'\s(?:class|style|id|role|dir|lang|decoding|loading|srcset|data-[\w-]+|'
                      r'width|height|title|rel|typeof|property)="[^"]*"', "", html, flags=re.I)
        html = re.sub(r"<a\b[^>]*?href=\"([^\"]*)\"[^>]*>", r'<a href="\1">', html, flags=re.I)

        def img_only(m):
            tag = m.group(0)
            src = re.search(r'src="([^"]*)"', tag)
            alt = re.search(r'alt="([^"]*)"', tag)
            if not src:
                return ""
            a = f' alt="{alt.group(1)}"' if alt else ""
            return f'<img src="{src.group(1)}"{a}>'

        html = re.sub(r"<img\b[^>]*>", img_only, html, flags=re.I)
        html = re.sub(r"<meta\b[^>]*>", "", html, flags=re.I)
        return html


def html_to_md(html, tmpdir, idx):
    if HAVE_MARKDOWNIFY:
        return _markdownify(html, heading_style="ATX", bullets="-",
                            escape_asterisks=False, escape_underscores=False,
                            strip_comments=True, wrap=False)
    # absolute paths: the cwd must not matter
    tmpdir = os.path.abspath(tmpdir)
    src = os.path.join(tmpdir, f"{idx}.html")
    dst = os.path.join(tmpdir, f"{idx}.md")
    with open(src, "w", encoding="utf-8") as f:
        f.write(html)
    p = subprocess.run(["pandoc", "-f", "html", "-t", "gfm", "--wrap=none", "-o", dst, src],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if p.returncode != 0 or not os.path.exists(dst):
        raise RuntimeError(f"pandoc failed (rc={p.returncode}) for {src}")
    with open(dst, encoding="utf-8") as f:
        return f.read()


def clean_md(md):
    # pandoc still emits a few block-level HTML leftovers; drop the ones that carry no content
    md = re.sub(r"^</?(?:div|span|p|section|figure|figcaption)[^>]*>\s*$", "", md, flags=re.M | re.I)
    md = re.sub(r"^Retrieved from .*$", "", md, flags=re.M)
    md = re.sub(r"\n{3,}", "\n\n", md)
    md = re.sub(r"[ \t]+\n", "\n", md)
    return md.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--api", default="https://peak.wiki.gg/api.php")
    ap.add_argument("--base", default="https://peak.wiki.gg")
    ap.add_argument("--dump", default="peak-dump")
    ap.add_argument("--out", default="peak-dump/markdown")
    ap.add_argument("--namespaces", default="0")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--resume", action="store_true",
                    help="skip pages whose .md is already on disk")
    ap.add_argument("--concurrency", type=int, default=2)
    ap.add_argument("--delay", type=float, default=1.0)
    ap.add_argument("--combined-name", default="PEAK-Wiki")
    ap.add_argument("--user-agent", default=UA_DEFAULT)
    args = ap.parse_args()

    api = Api(args.api, args.user_agent, delay=args.delay)
    image_dir = os.path.join(args.dump, "images")
    pages_dir = os.path.join(args.out, "pages")
    tmpdir = os.path.join(args.out, ".tmp")
    for d in (pages_dir, tmpdir):
        os.makedirs(d, exist_ok=True)

    namespaces = [int(x) for x in args.namespaces.split(",") if x.strip() != ""]
    by_ns = {ns: list_titles(api, ns) for ns in namespaces}
    all_titles = {t for ts in by_ns.values() for t in ts}
    log(f"pages to convert: {len(all_titles)}")

    rewriter = Rewriter(args.base, image_dir, all_titles,
                        img_prefix="../../images/", page_prefix="")
    results = {}
    lock = threading.Lock()
    jobs = [(ns, t) for ns, ts in by_ns.items() for t in ts]
    jobs = jobs[args.offset:]
    if args.limit:
        jobs = jobs[:args.limit]
    q = list(enumerate(jobs))
    counter = {"i": 0}
    t0 = time.time()

    def worker():
        while True:
            with lock:
                if not q:
                    return
                i, (ns, title) = q.pop(0)
            out_path = os.path.join(pages_dir, slug(title) + ".md")
            if args.resume and os.path.exists(out_path):
                with lock:
                    results[title] = {"ns": ns, "path": out_path, "chars": 0,
                                      "revid": None, "cached": True}
                continue
            try:
                d = api.json(action="parse", page=title, prop="text|revid",
                             disableeditsection="1", disabletoc="1", redirects="1")
                if "error" in d:
                    log(f"  ! {title}: {d['error'].get('code')}")
                    continue
                parse = d["parse"]
                md = clean_md(html_to_md(rewriter.html(parse["text"]), tmpdir, i))
                body = f"# {title}\n\n{md}\n"
                path = os.path.join(pages_dir, slug(title) + ".md")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(f"---\ntitle: {json.dumps(title, ensure_ascii=False)}\n"
                            f"source: {args.base}/wiki/{urllib.parse.quote(title.replace(' ', '_'))}\n"
                            f"pageid: {parse.get('pageid')}\nrevid: {parse.get('revid')}\n"
                            f"namespace: {ns}\n---\n\n{body}")
                with lock:
                    results[title] = {"ns": ns, "path": path, "chars": len(body),
                                      "revid": parse.get("revid")}
                    counter["i"] += 1
                    if counter["i"] % 50 == 0:
                        log(f"  {counter['i']}/{len(jobs)} pages")
            except Exception as e:  # noqa: BLE001
                log(f"  ! {title}: {e!r}")
                with lock:
                    results[title] = {"ns": ns, "error": repr(e)}

    threads = [threading.Thread(target=worker) for _ in range(args.concurrency)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    el = time.time() - t0

    ok = {t: r for t, r in results.items() if "error" not in r}
    log(f"converted {len(ok)}/{len(jobs)} pages in {el:.0f}s "
        f"({api.requests} api requests, {api.throttled} throttled)")

    # Build the index and the combined file from everything on disk, so chunked runs
    # (--offset/--limit) still produce a complete pair.
    present = []
    for fn in sorted(os.listdir(pages_dir)):
        if not fn.endswith(".md"):
            continue
        text = open(os.path.join(pages_dir, fn), encoding="utf-8").read()
        m = re.match(r"^---\n(.*?)\n---\n\n", text, re.S)
        fm = dict(re.findall(r"^(\w+): (.*)$", m.group(1), re.M)) if m else {}
        try:
            title = json.loads(fm.get("title", f'"{fn[:-3]}"'))
        except Exception:  # noqa: BLE001
            title = fn[:-3]
        present.append((int(fm.get("namespace", 0)), title, text, len(text)))

    combined = [f"# {args.combined_name}\n",
                f"Source: {args.base}  ",
                f"Pages: {len(present)}  ",
                "License: CC BY-SA 4.0 — attribute the PEAK Wiki contributors.\n"]
    for ns in namespaces:
        for n, title, text, _ in present:
            if n != ns:
                continue
            body = re.sub(r"^---\n.*?\n---\n\n", "", text, flags=re.S)
            body = body.replace("../../images/", "../images/")
            combined.append(body.rstrip() + "\n\n---\n")
    comb_path = os.path.join(args.out, f"{args.combined_name}.md")
    with open(comb_path, "w", encoding="utf-8") as f:
        f.write("\n".join(combined))

    index = [f"# {args.combined_name} — Index\n", f"{len(present)} pages\n"]
    for ns in namespaces:
        index.append(f"\n## Namespace {ns}\n")
        for n, title, _, size in sorted(present, key=lambda x: x[1]):
            if n != ns:
                continue
            index.append(f"- [{title}](pages/{urllib.parse.quote(slug(title))}.md) — {size} chars")
    with open(os.path.join(args.out, "INDEX.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(index) + "\n")

    report = {
        "out": args.out, "pages_ok": len(ok), "pages_total": len(jobs),
        "seconds": round(el, 1), "api_requests": api.requests, "throttled_429": api.throttled,
        "internal_links_rewritten": rewriter.rewritten_links,
        "combined": comb_path, "combined_bytes": os.path.getsize(comb_path),
        "missing_image_count": len(rewriter.missing_images),
        "missing_images": sorted(rewriter.missing_images)[:50],
        "errors": [{"title": t, "error": r["error"]} for t, r in results.items() if "error" in r],
    }
    with open(os.path.join(args.out, "convert-summary.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    log(json.dumps({k: v for k, v in report.items() if k != "errors"},
                   indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

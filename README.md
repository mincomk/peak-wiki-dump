# PEAK Wiki dump

A local copy of **https://peak.wiki.gg** (the PEAK game wiki, MediaWiki 1.43.6 on the wiki.gg
platform), taken on **2026-10-15** with the `peak.wiki.gg/api.php` read API.

## Contents

| Path | What it is |
|---|---|
| `markdown/pages/<Title>.md` | 357 main-namespace articles rendered to Markdown, one file per article, with YAML front matter (title, source URL, pageid, revid) |
| `markdown/INDEX.md` | every article, linked |
| `markdown/PEAK-Wiki.md` | all 357 articles concatenated into a single document (1.9 MB) |
| `images/` | all 1,193 local media files (611.6 MB), sha1-verified against the API |
| `wikitext/pages.jsonl` | raw wikitext of every page: `ns, title, pageid, revid, timestamp, text` (3,033 pages) |
| `wikitext/text-<ns>-<name>.xml` | the same pages as per-namespace XML |

Article bodies were rendered through `action=parse` (so templates, infoboxes and tables are
resolved), then converted HTML -> GFM Markdown. **40,022 internal links** were rewritten to
sibling `.md` files; image links point at `../../images/<file>`, so `markdown/` and `images/`
must stay together.

## How it was made

```bash
# 1. text + media
python3 peak_dump.py --out peak-dump --concurrency 4 --delay 1.0

# 2. articles -> markdown
python3 peak_md.py --dump peak-dump --out peak-dump/markdown \
    --namespaces 0 --concurrency 4 --delay 0.35
```

`peak_md.py` is included as `tools/wikitext-to-markdown.py` and `peak_dump.py` as
`tools/wiki-dump.py`. Both were written for this dump; `--namespaces 10,828,14` converts the
template/module/category namespaces the same way.

Two things worth knowing if you re-run them:

- Media URLs from the API carry a `?<hash>` cache-buster that Cloudflare answers with a
  **recompressed** image. A unique query string forces a cache miss, which returns the
  uploaded original - that is what `images/` holds (`sha1` in `media-manifest.jsonl`).
- `list=allpages` + `prop=revisions` is the reliable way to walk pages; the `action=query&export=1`
  route hands back no continuation token and silently stops after ~881 of 1,324 pages in the
  File namespace.

## Licence and source

The content is from https://peak.wiki.gg and is licensed **CC BY-SA 4.0** - when you reuse it,
attribute the PEAK Wiki contributors. This repository is a private working copy, not a
publication; the wiki's `robots.txt` disallows automated collection of `/api.php` and sets
`Content-Signal: ai-train=no, use=reference`.

`media-manifest.jsonl` (in `wikitext/`) records every image's original URL, size and sha1.

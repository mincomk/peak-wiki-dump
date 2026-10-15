#!/usr/bin/env python3
"""Zip the whole PEAK Wiki dump (markdown + media + wikitext) into one archive.

Images are already compressed, so they go in STORED; text goes in DEFLATED.
"""

import os
import re
import shutil
import sys
import zipfile

ROOT = "peak-dump"
OUT = "PEAK-Wiki.zip"
TOP = "PEAK-Wiki"

README = """# PEAK Wiki dump — peak.wiki.gg

Taken 2026-10-15 by Attacca.

## Contents
- `markdown/`   — 357 main-namespace articles as Markdown
  - `pages/<Title>.md`  one file per article
  - `INDEX.md`          every article, linked
  - `PEAK-Wiki.md`      all articles concatenated into one document
- `images/`     — all 1,193 local media files (611.6 MB), sha1-verified against the wiki API
- `wikitext/`   — raw wikitext of all 3,033 pages
  - `pages.jsonl`       one JSON object per page: ns, title, pageid, revid, timestamp, text
  - `text-<ns>-<name>.xml`  per-namespace XML

## Links
Image links in `markdown/pages/*.md` are `../../images/<file>` and in
`markdown/PEAK-Wiki.md` they are `../images/<file>`, so **keep this folder
structure intact** — if you move the Markdown, move `images/` with it.
Internal article links are percent-encoded, e.g. `Stamina%20bar.md` -> `Stamina bar.md`.

## Source and licence
Content comes from https://peak.wiki.gg and is licensed **CC BY-SA 4.0**.
Attribute the PEAK Wiki contributors (and the wiki.gg platform) when you reuse it.
robots.txt on that wiki disallows automated collection of /api.php and sets
`Content-Signal: ai-train=no` — this dump is a local copy, not a training corpus.
"""

WINDOWS_BAD = re.compile(r'[<>:"|?*]')


def main():
    if os.path.exists(OUT):
        os.remove(OUT)
    n_files = n_bytes = 0
    bad_names = []
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as z:
        z.writestr(f"{TOP}/README.md", README)

        def add(src, arc, compress):
            nonlocal n_files, n_bytes
            for base, _dirs, files in os.walk(src):
                for f in files:
                    p = os.path.join(base, f)
                    rel = os.path.relpath(p, src)
                    z.write(p, f"{TOP}/{arc}/{rel}", compress_type=compress)
                    n_files += 1
                    n_bytes += os.path.getsize(p)

        add(os.path.join(ROOT, "markdown"), "markdown", zipfile.ZIP_DEFLATED)
        print(f"markdown done: {n_files} files", flush=True)
        add(os.path.join(ROOT, "images"), "images", zipfile.ZIP_STORED)
        print(f"images done: {n_files} files", flush=True)

        wikitext = os.path.join(ROOT, "pages.jsonl")
        if os.path.exists(wikitext):
            z.write(wikitext, f"{TOP}/wikitext/pages.jsonl")
            n_files += 1
            n_bytes += os.path.getsize(wikitext)
        for f in sorted(os.listdir(ROOT)):
            if f.startswith("text-") and f.endswith(".xml"):
                z.write(os.path.join(ROOT, f), f"{TOP}/wikitext/{f}")
                n_files += 1
                n_bytes += os.path.getsize(os.path.join(ROOT, f))

        for info in z.infolist():
            if WINDOWS_BAD.search(os.path.basename(info.filename)):
                bad_names.append(info.filename)

    print(f"wrote {OUT}: {n_files} files, {n_bytes/1e6:.1f} MB raw, "
          f"{os.path.getsize(OUT)/1e6:.1f} MB zipped")
    if bad_names:
        print(f"WARNING: {len(bad_names)} entries contain characters Windows cannot extract:")
        for b in bad_names[:10]:
            print("   ", b)
    else:
        print("no Windows-illegal filenames")


if __name__ == "__main__":
    main()

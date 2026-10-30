#!/usr/bin/env python3
"""Fail on relative Markdown links that point at nothing in the Git tree.

Only tracked files count as targets: a link into gitignored runs/, datasets/
or outputs/ resolves on one machine and 404s on GitHub, so it is reported too.
The one exception is bench/, the data checkout (docs/guides/data.md): links
into it are checked against the checkout when it is present and skipped when
it is not.
Usage: scripts/check-doc-links.py [--ignored-ok]
"""
import os
import re
import subprocess
import sys

LINK = re.compile(r"\]\(([^)\s]+)\)")
# Inline code is not rendered as a link: `[text](url)` documents the syntax.
CODE_SPAN = re.compile(r"`[^`]*`")
SKIP_PREFIXES = ("third_party/",)


def main() -> int:
    root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
    os.chdir(root)
    # quotePath off: non-ASCII filenames must match link targets byte-for-byte
    tracked = set(subprocess.check_output(
        ["git", "-c", "core.quotePath=false", "ls-files"], text=True).splitlines())
    dirs = {os.path.dirname(p) for p in tracked}
    for d in list(dirs):
        while d:
            d = os.path.dirname(d)
            dirs.add(d)
    bad = 0
    have_bench = os.path.isdir("bench")
    for md in sorted(p for p in tracked if p.endswith(".md") and not p.startswith(SKIP_PREFIXES)):
        with open(md, encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, 1):
                for target in LINK.findall(CODE_SPAN.sub("", line)):
                    if re.match(r"^[a-z][a-z0-9+.-]*:|^#|^/", target):
                        continue
                    path = target.split("#", 1)[0]
                    if not path:
                        continue
                    resolved = os.path.normpath(os.path.join(os.path.dirname(md), path))
                    if resolved in tracked or resolved in dirs:
                        continue
                    if resolved.startswith("bench/") and (not have_bench or os.path.exists(resolved)):
                        continue
                    print(f"{md}:{lineno}: {target}")
                    bad += 1
    print(f"{bad} broken link(s)", file=sys.stderr)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

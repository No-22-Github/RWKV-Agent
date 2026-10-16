#!/usr/bin/env python3
"""Builds the 130 b21d cases (v2.1): confirm before destructive ops, ask when ambiguous, answer from local files.

    cd bench/distill/tools/b21d && python3 build.py
"""
import sys

from common import META
import p1
import p1a, p1b, p1c  # noqa: F401
BUILDERS = list(p1.BUILDERS)
try:
    import p2a, p2b, p2c, p2d  # noqa: F401
    import p2
    BUILDERS += p2.BUILDERS
except ImportError as e:
    print("part 2 not built:", e)
try:
    import p3a, p3b, p3c, p3d, p3e  # noqa: F401
    import p3
    BUILDERS += p3.BUILDERS
except ImportError as e:
    print("part 3 not built:", e)


def main():
    for b in BUILDERS:
        b()
    kinds = {}
    for m in META.values():
        kinds[m["kind"]] = kinds.get(m["kind"], 0) + 1
    lv = {}
    for m in META.values():
        lv[m["level"]] = lv.get(m["level"], 0) + 1
    print("cases %d %s levels %s zh %d multi %d policy %d" % (len(META), kinds, lv, sum(m["lang"] == "zh" for m in META.values()),
          sum(m["turns"] > 1 for m in META.values()), sum(m["policy"] for m in META.values())))
    return 0


if __name__ == "__main__":
    sys.exit(main())

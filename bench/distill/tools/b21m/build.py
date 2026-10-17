#!/usr/bin/env python3
"""Builds the 60 b21m cases (v2.1): confirm destructive ops, ask when ambiguous, undo a change.

    cd bench/distill/tools/b21m && python3 build.py
"""
import sys

from common import META
import p0
import q1, q2, q3, r1, r2, r3, u1, u2, u3  # noqa: F401


def main():
    for b in p0.BUILDERS:
        b()
    kinds, lv = {}, {}
    for m in META.values():
        kinds[m["kind"]] = kinds.get(m["kind"], 0) + 1
        lv[m["level"]] = lv.get(m["level"], 0) + 1
    print("cases %d %s levels %s zh %d multi %d policy %d" % (len(META), kinds, lv, sum(m["lang"] == "zh" for m in META.values()),
          sum(m["turns"] > 1 for m in META.values()), sum(m["policy"] for m in META.values())))
    return 0


if __name__ == "__main__":
    sys.exit(main())

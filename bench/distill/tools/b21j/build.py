#!/usr/bin/env python3
"""Builds the 80 b21j cases (v2.1, nt-33101..33180).  cd bench/distill/tools/b21j && python3 build.py"""
import importlib
import sys

import common

MODS = ["r1", "r2", "c1", "c2", "f1", "f2", "u1", "s1", "b1"]


def main():
    for n in MODS:
        try:
            m = importlib.import_module(n)
        except ModuleNotFoundError as e:
            if e.name != n:
                raise
            continue
        m.build()
    ids = sorted(common.META)
    subs = {}
    for c in ids:
        subs[common.META[c]["sub"]] = subs.get(common.META[c]["sub"], 0) + 1
    zh = sum(common.META[c]["zh"] for c in ids)
    mu = sum(common.META[c]["multi"] for c in ids)
    l0 = sum(common.META[c]["level"] == "L0" for c in ids)
    print("cases", len(ids), subs, "zh", zh, "multi", mu, "L0", l0)


if __name__ == "__main__":
    sys.exit(main())

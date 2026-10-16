#!/usr/bin/env python3
"""Builds b21c (v2.1, cases 31201-31280): say "not there" when the lookup comes up empty.

    cd bench/distill/tools/b21c && python3 build.py [--stats]
"""
import argparse
import importlib
import sys
from collections import Counter

from common import META

MODULES = ["a_key", "b_file", "c_stale", "d_conflict", "e_partial"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stats", action="store_true")
    a = ap.parse_args()
    for name in MODULES:
        try:
            mod = importlib.import_module(name)
        except ModuleNotFoundError:
            print("skip", name)
            continue
        for b in mod.BUILDERS:
            b()
    n = len(META)
    zh = sum(1 for m in META.values() if m["zh"])
    mt = sum(1 for m in META.values() if m["turns"] > 1)
    print("cases %d zh %d multi %d" % (n, zh, mt))
    if a.stats:
        print("sub", dict(Counter(m["sub"] for m in META.values())))
        print("level", dict(Counter(m["level"] for m in META.values())))
        print("policy", dict(Counter(m["pol"] for m in META.values())))
    sys.exit(0)


if __name__ == "__main__":
    main()

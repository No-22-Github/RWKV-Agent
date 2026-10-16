#!/usr/bin/env python3
"""Builds the 75 b21b cases (v2.1). cd bench/distill/tools/b21b && python3 build.py"""
import importlib
import sys

from common import META

MODS = ["s1a", "s1b", "s2", "s3", "s4", "s5"]


def main():
    for name in MODS:
        try:
            m = importlib.import_module(name)
        except ModuleNotFoundError as e:
            if e.name == name:
                continue
            raise
        for b in m.BUILDERS:
            b()
    subs = {}
    for v in META.values():
        subs[v["sub"]] = subs.get(v["sub"], 0) + 1
    lv = {}
    for v in META.values():
        lv[v["level"]] = lv.get(v["level"], 0) + 1
    pol = {}
    for v in META.values():
        pol[v["policy"]] = pol.get(v["policy"], 0) + 1
    print("policy", pol)
    print("cases %d subs %s levels %s zh %d multi %d" % (len(META), subs, lv, sum(v["zh"] for v in META.values()),
          sum(v["turns"] > 1 for v in META.values())))


if __name__ == "__main__":
    sys.exit(main())

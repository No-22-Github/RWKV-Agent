#!/usr/bin/env python3
"""Builds the 75 b21k cases (v2.1, ids 33201-33275). cd bench/distill/tools/b21k && python3 build.py"""
import importlib
import sys

from common import META

MODS = ["s1a", "s1b", "s2a", "s2b", "s3a", "s3b", "s4a", "s4b"]


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
    subs, lv, pol = {}, {}, {}
    for v in META.values():
        subs[v["sub"]] = subs.get(v["sub"], 0) + 1
        lv[v["level"]] = lv.get(v["level"], 0) + 1
        pol[v["policy"]] = pol.get(v["policy"], 0) + 1
    print("cases %d subs %s levels %s zh %d multi %d never %d" % (
        len(META), subs, lv, sum(v["zh"] for v in META.values()),
        sum(v["turns"] > 1 for v in META.values()), sum(v["never"] for v in META.values())))
    print("policy", pol)


if __name__ == "__main__":
    sys.exit(main())

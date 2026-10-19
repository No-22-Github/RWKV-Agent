#!/usr/bin/env python3
"""Builds the 60 b22c cases (v2.2, ids 34201-34260). cd bench/distill/tools/b22c && python3 build.py"""
import importlib
import sys

import common

MODS = ["c1a", "c1b", "c1l1", "c1l2", "c2a", "c2b", "c2c", "c0a", "c0b"]


def main():
    for name in MODS:
        try:
            m = importlib.import_module(name)
        except ModuleNotFoundError as e:
            if e.name != name:
                raise
            continue
        m.build()
    meta = common.META
    by = {}
    for cid, m in meta.items():
        by.setdefault(m["sub"], []).append(m)
    print("cases", len(meta))
    for sub in sorted(by):
        ms = by[sub]
        print(sub, len(ms), "zh", sum(x["zh"] for x in ms), "multi", sum(x["turns"] > 1 for x in ms),
              "avg_prompt_chars %.0f" % (sum(x["plen"] for x in ms) / len(ms)),
              "levels", {l: sum(1 for x in ms if x["level"] == l) for l in sorted({x["level"] for x in ms})},
              "scen", {s: sum(1 for x in ms if x["scen"] == s) for s in sorted({x["scen"] for x in ms})})
    return 0


if __name__ == "__main__":
    sys.exit(main())

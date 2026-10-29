#!/usr/bin/env python3
"""Builds the 60 b23d cases (v2.3, 3-4 user-turn conversations, ids 35201-35260).

    cd bench/distill/tools/b23d && python3 build.py   # no randomness; reruns are byte-identical
"""
import importlib
import sys

import common

MODS = ["d1a", "d1b", "d1c", "d2a", "d2b"]


def main():
    for name in MODS:
        try:
            m = importlib.import_module(name)
        except ModuleNotFoundError as e:
            if e.name != name:
                raise
            continue
        for b in m.B:
            b()
    stats = {}
    for c, m in common.META.items():
        s = stats.setdefault(m["sub"], dict(n=0, zh=0, chars=0, tt={}, lv={}))
        s["n"] += 1
        s["zh"] += m["zh"]
        s["chars"] += m["chars"]
        s["tt"][m["tt"]] = s["tt"].get(m["tt"], 0) + 1
        s["lv"][m["level"]] = s["lv"].get(m["level"], 0) + 1
    for k in sorted(stats):
        s = stats[k]
        print("%s n=%d zh=%d avg_chars=%.1f tt=%s lv=%s" % (k, s["n"], s["zh"], s["chars"] / s["n"], s["tt"], s["lv"]))
    print("total", len(common.META))
    return 0


if __name__ == "__main__":
    sys.exit(main())

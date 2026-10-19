#!/usr/bin/env python3
"""Builds the 90 b22a cases (v2.2, local search empty -> go online, ids 34001-34090).

    cd bench/distill/tools/b22a && python3 build.py   # no randomness; reruns are byte-identical
"""
import importlib
import sys

import common

MODS = ["a1_x", "a1_y", "a1_z", "a1_w", "a2_x", "a2_y", "a0_x", "a0_y"]


def main():
    for name in MODS:
        try:
            m = importlib.import_module(name)
        except ModuleNotFoundError as e:
            if e.name != name:
                raise
            continue
        m.build()
    stats = {}
    for c, m in common.META.items():
        s = stats.setdefault(m["sub"], dict(n=0, zh=0, multi=0, chars=0, web=0, lv={}))
        s["n"] += 1
        s["zh"] += m["zh"]
        s["multi"] += m["turns"] > 1
        s["chars"] += m["chars"]
        s["web"] += m["scen"] == "web"
        s["lv"][m["level"]] = s["lv"].get(m["level"], 0) + 1
    for k in sorted(stats):
        s = stats[k]
        print("%s n=%d zh=%d multi=%d avg_chars=%.1f web=%d hyb=%d levels=%s" % (k, s["n"], s["zh"], s["multi"], s["chars"] / s["n"], s["web"], s["n"] - s["web"], s["lv"]))
    print("total", len(common.META))
    return 0


if __name__ == "__main__":
    sys.exit(main())

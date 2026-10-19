#!/usr/bin/env python3
"""Builds the 70 b22d cases (v2.2, ids 34301-34370).

    cd bench/distill/tools/b22d && python3 build.py
"""
import importlib
import sys

import common

MODS = ["d1a", "d1b", "d1c", "d2a", "d2b", "d0a", "d0b"]


def main():
    for name in MODS:
        try:
            m = importlib.import_module(name)
        except ModuleNotFoundError as e:
            if e.name != name:
                raise
            continue
        m.build()
    if common.SIDE:
        common.SIDE[0].close()
    ids = sorted(common.META)
    stat = {}
    for c in ids:
        m = common.META[c]
        s = stat.setdefault(m["sub"], {"n": 0, "zh": 0, "multi": 0, "plen": 0, "pol": {}})
        s["n"] += 1
        s["zh"] += m["zh"]
        s["multi"] += m["multi"]
        s["plen"] += m["plen"]
        s["pol"][m["policy"]] = s["pol"].get(m["policy"], 0) + 1
    print("cases", len(ids))
    for k in sorted(stat):
        s = stat[k]
        print(k, "n=%d zh=%d multi=%d avg_prompt_chars=%.0f policy=%s" % (s["n"], s["zh"], s["multi"], s["plen"] / s["n"], s["pol"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())

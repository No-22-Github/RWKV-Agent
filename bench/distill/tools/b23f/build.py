#!/usr/bin/env python3
"""Builds the 50 b23f cases (v2.3, ids 35401-35450).

    cd bench/distill/tools/b23f && python3 build.py
"""
import importlib
import sys

import common


def main():
    for name in ["f1", "f2", "f0"]:
        importlib.import_module(name).build()
    if common.SIDE:
        common.SIDE[0].close()
    stat = {}
    for c in sorted(common.META):
        m = common.META[c]
        s = stat.setdefault(m["sub"], {"n": 0, "zh": 0, "multi": 0, "plen": 0, "L0": 0})
        s["n"] += 1
        s["zh"] += m["zh"]
        s["multi"] += m["multi"]
        s["plen"] += m["plen"]
        s["L0"] += m["level"] == "L0"
    print("cases", len(common.META))
    for k in sorted(stat):
        s = stat[k]
        print(k, "n=%d zh=%d en=%d multi=%d L0=%d avg_prompt_chars=%.0f" % (s["n"], s["zh"], s["n"] - s["zh"], s["multi"], s["L0"], s["plen"] / s["n"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())

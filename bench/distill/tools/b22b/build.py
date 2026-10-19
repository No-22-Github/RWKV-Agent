#!/usr/bin/env python3
"""Builds the 50 b22b cases (v2.2, web, ids 34101-34150).

    cd bench/distill/tools/b22b && python3 build.py
"""
import importlib
import sys

import common

MODS = ["b1a", "b1b", "b1c", "b2", "b3", "b3b"]


def main():
    for name in MODS:
        try:
            m = importlib.import_module(name)
        except ModuleNotFoundError as e:
            if e.name != name:
                raise
            continue
        m.build()
    subs = {}
    for c, m in common.META.items():
        s = subs.setdefault(m["sub"], dict(n=0, zh=0, multi=0, chars=0))
        s["n"] += 1
        s["zh"] += m["zh"]
        s["multi"] += m["turns"] > 1
        s["chars"] += m["len"]
    lv = {}
    for m in common.META.values():
        lv[m["level"]] = lv.get(m["level"], 0) + 1
    print("cases %d" % len(common.META))
    for k in sorted(subs):
        s = subs[k]
        print(k, "n=%d zh=%d multi=%d avg_chars=%.0f" % (s["n"], s["zh"], s["multi"], s["chars"] / s["n"]))
    print("levels", lv)
    return 0


if __name__ == "__main__":
    sys.exit(main())

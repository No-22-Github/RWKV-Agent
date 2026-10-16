#!/usr/bin/env python3
"""Builds the 50 b21h cases (v2.1, ids 32301-32350).

    cd bench/distill/tools/b21h && python3 build.py
"""
import importlib
import sys

import common

MODS = ["s1a", "s1b", "s2a", "s2b", "s3", "s4", "s5a", "s5b"]


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
    bad = common.run_checks()
    for x in bad:
        print("CHECK FAIL", x)
    ids = sorted(common.META)
    subs, zh, multi, pol = {}, 0, 0, {}
    for c in ids:
        m = common.META[c]
        subs[m["sub"]] = subs.get(m["sub"], 0) + 1
        zh += m["lang"] == "zh"
        multi += m["turns"] > 1
        pol[m["pol"]] = pol.get(m["pol"], 0) + 1
    print("cases %d %s zh %d multi %d policy %s" % (len(ids), subs, zh, multi, pol))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Builds the 70 b21o cases (v2.1, ids 33601-33670).

    cd bench/distill/tools/b21o && python3 build.py
"""
import importlib
import sys

import common

MODS = ["w1", "w2", "d1", "d2", "c1", "c2", "q1", "q2", "f1", "f2"]


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
    ids = sorted(common.META)
    subs, zh, multi, lv, pol = {}, 0, 0, {}, {}
    for c in ids:
        m = common.META[c]
        subs[m["sub"]] = subs.get(m["sub"], 0) + 1
        zh += m["zh"]
        multi += m["turns"] > 1
        lv[m["level"]] = lv.get(m["level"], 0) + 1
        pol[m["policy"]] = pol.get(m["policy"], 0) + 1
    print("cases %d %s zh %d multi %d levels %s" % (len(ids), subs, zh, multi, lv))
    print("policy", pol)
    return 0


if __name__ == "__main__":
    sys.exit(main())

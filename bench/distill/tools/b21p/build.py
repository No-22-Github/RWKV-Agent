#!/usr/bin/env python3
"""Builds the 70 b21p cases (v2.1, ids 33701-33770).

    cd bench/distill/tools/b21p && python3 build.py
"""
import importlib
import sys

import common

MODS = ["f1", "f2", "f3", "f4", "l1", "l2", "l3", "l4"]


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
    subs, zh, multi = {}, 0, 0
    for c in ids:
        m = common.META[c]
        subs[m["sub"]] = subs.get(m["sub"], 0) + 1
        zh += m["lang"] == "zh"
        multi += m["turns"] > 1
    print("cases %d %s zh %d multi %d" % (len(ids), subs, zh, multi))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

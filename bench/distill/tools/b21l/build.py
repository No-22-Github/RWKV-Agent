#!/usr/bin/env python3
"""Builds the 80 b21l cases (v2.1 wave 3, ids 33301-33380).

    cd bench/distill/tools/b21l && python3 build.py
"""
import importlib
import sys

import common

MODS = ["a_webedit", "b_write", "c_calc", "d_comp", "e_multi"]


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
    subs, zh, multi, pol = {}, 0, 0, {}
    for c in ids:
        m = common.META[c]
        subs[m["sub"]] = subs.get(m["sub"], 0) + 1
        zh += m["zh"]
        multi += m["turns"] > 1
    print("cases %d %s zh %d multi %d" % (len(ids), subs, zh, multi))
    return 0


if __name__ == "__main__":
    sys.exit(main())

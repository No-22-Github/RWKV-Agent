#!/usr/bin/env python3
"""Builds the 80 b21i cases (v2.1 wave 3, web, ids 33001-33080).

    cd bench/distill/tools/b21i && python3 build.py
"""
import importlib
import sys

import common

MODS = ["a_summary", "b_compare", "c_lookup", "d_latest", "e_error", "f_deprec", "g_fail"]


def main():
    for name in MODS:
        try:
            m = importlib.import_module(name)
        except ModuleNotFoundError as e:
            if e.name != name:
                raise
            continue
        m.build()
    ids = sorted(common.META)
    subs, zh, multi, lv, pol = {}, 0, 0, {}, {}
    for c in ids:
        m = common.META[c]
        subs[m["tt"]] = subs.get(m["tt"], 0) + 1
        zh += m["zh"]
        multi += m["turns"] > 1
        lv[m["level"]] = lv.get(m["level"], 0) + 1
        pol[m["pol"]] = pol.get(m["pol"], 0) + 1
    print("cases %d %s zh %d multi %d levels %s policy %s" % (len(ids), subs, zh, multi, lv, pol))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Builds the 60 b23e cases (v2.3, ids 35301-35360).

    cd bench/distill/tools/b23e && python3 build.py
"""
import sys

import common
import e0
import e1
import e2


def main():
    bad = common.selftest()
    for x in bad:
        print("SELFTEST FAIL", x)
    for mod in (e1, e2, e0):
        for b in mod.B:
            b()
    ids = sorted(common.META)
    subs, zh, multi = {}, {}, {}
    plen = {}
    for c in ids:
        m = common.META[c]
        s = m["sub"]
        subs[s] = subs.get(s, 0) + 1
        zh[s] = zh.get(s, 0) + (m["lang"] == "zh")
        multi[s] = multi.get(s, 0) + (m["turns"] > 1)
        plen.setdefault(s, []).append(m["plen"])
    print("cases", len(ids), subs)
    print("zh", zh, "multi", multi, "avg prompt chars", {k: round(sum(v) / len(v)) for k, v in plen.items()})
    print("levels", {l: sum(1 for c in ids if common.META[c]["level"] == l) for l in ("L0", "L1", "L2", "L3")})
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

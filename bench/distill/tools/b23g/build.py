#!/usr/bin/env python3
"""Builds the 40 b23g cases (v2.3, ids 35501-35540).

    cd bench/distill/tools/b23g && python3 build.py
"""
import sys

import common
import g0
import g1_cfg
import g1_code
import g1_docs
import g1_logs


def main():
    for mod in (g1_docs, g1_logs, g1_cfg, g1_code, g0):
        for b in mod.B:
            b()
    ids = sorted(common.META)
    subs, zh, multi, plen, lines = {}, {}, {}, {}, {}
    for c in ids:
        m = common.META[c]
        s = m["sub"]
        subs[s] = subs.get(s, 0) + 1
        zh[s] = zh.get(s, 0) + (m["lang"] == "zh")
        multi[s] = multi.get(s, 0) + (m["turns"] > 1)
        plen.setdefault(s, []).append(m["plen"])
        lines.setdefault(s, []).append(m["lines"])
    print("cases", len(ids), subs)
    print("zh", zh, "multi", multi, "avg prompt chars", {k: round(sum(v) / len(v)) for k, v in plen.items()})
    print("lines min/max", {k: (min(v), max(v)) for k, v in lines.items()})
    return 0


if __name__ == "__main__":
    sys.exit(main())

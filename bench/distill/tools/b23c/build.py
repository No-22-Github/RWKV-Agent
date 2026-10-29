#!/usr/bin/env python3
"""Builds the 70 b23c cases (v2.3): ask first when key information is missing (C1), act when it is not (C0).

    cd bench/distill/tools/b23c && python3 build.py
"""
import sys

from common import META
import p_cfg, p_doc, p_hyb, p_fs


def main():
    for m in (p_cfg, p_doc, p_hyb, p_fs):
        for b in m.BUILDERS:
            b()
    by = {}
    for cid, m in META.items():
        d = by.setdefault(m["sub"], {"n": 0, "zh": 0, "multi": 0, "L0": 0, "plen": 0})
        d["n"] += 1
        d["zh"] += m["lang"] == "zh"
        d["multi"] += m["turns"] > 1
        d["L0"] += m["level"] == "L0"
        d["plen"] += m["plen"]
    for s, d in sorted(by.items()):
        print(s, d, "avg_prompt %.0f" % (d["plen"] / d["n"]))
    print("total", len(META), "multi", sum(m["turns"] > 1 for m in META.values()))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Builds the 80 b23b cases (v2.3, local-first control, ids 35001-35080).

    cd bench/distill/tools/b23b && python3 build.py   # no randomness; reruns are byte-identical
"""
import sys

import common



def main():
    import pairs_en, pairs_zh, single, b2_all
    pairs = pairs_en.PAIRS + pairs_zh.PAIRS
    for b1kw, _ in pairs:
        common.b1(**b1kw)
    for kw in single.S:
        common.b1(**kw)
    b2_all.build()
    for _, b0kw in pairs:
        common.b0(**b0kw)
    stats = {}
    for c, m in common.META.items():
        s = stats.setdefault(m["sub"], dict(n=0, zh=0, multi=0, chars=0, lv={}))
        s["n"] += 1
        s["zh"] += m["zh"]
        s["multi"] += m["turns"] > 1
        s["chars"] += m["chars"]
        s["lv"][m["level"]] = s["lv"].get(m["level"], 0) + 1
    for k in sorted(stats):
        s = stats[k]
        print("%s n=%d zh=%d en=%d multi=%d avg_chars=%.1f levels=%s" % (k, s["n"], s["zh"], s["n"] - s["zh"], s["multi"], s["chars"] / s["n"], s["lv"]))
    print("total", len(common.META))
    return 0


if __name__ == "__main__":
    sys.exit(main())

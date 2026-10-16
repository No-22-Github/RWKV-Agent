#!/usr/bin/env python3
"""Builds the 50 b21g cases (v2.1, ids 32201-32250) and replays every bash reference in the just-bash sidecar.

    cd bench/distill/tools/b21g && python3 build.py
"""
import sys

import common
import a1, a2, b1, c1, c2, d1, e1  # noqa: F401
MODS = []


def main():
    for b in common.B:
        b()
    sc = common.Sidecar()
    bad = common.check_refs(sc)
    sc.close()
    m = common.META
    lv, subs = {}, {}
    for c in m.values():
        lv[c["level"]] = lv.get(c["level"], 0) + 1
        subs[c["sub"]] = subs.get(c["sub"], 0) + 1
    print("cases %d %s levels %s zh %d multi %d forbid %d" % (len(m), subs, lv, sum(c["lang"] == "zh" for c in m.values()),
          sum(c["turns"] > 1 for c in m.values()), sum(c["forbid"] for c in m.values())))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

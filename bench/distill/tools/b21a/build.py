#!/usr/bin/env python3
"""Builds the 75 b21a cases (v2.1, ids 31001-31075).

    cd bench/distill/tools/b21a && python3 build.py
"""
import sys

from common import META
import s1a, s1b, s2, s3, s4, s5a, s5b

# ids come from each builder's make() call; s5b also imports chk from s5a
MODS = [s1a, s1b, s2, s3, s4, s5a, s5b]


def main():
    for m in MODS:
        for b in m.B:
            b()
    ids = sorted(META)
    subs, zh, multi, pol, lv = {}, 0, 0, 0, {}
    for c in ids:
        m = META[c]
        subs[m["sub"]] = subs.get(m["sub"], 0) + 1
        zh += m["lang"] == "zh"
        multi += m["turns"] > 1
        pol += m["policy"]
        lv[m["level"]] = lv.get(m["level"], 0) + 1
    print("cases %d %s zh %d multi %d policy %d levels %s" % (len(ids), subs, zh, multi, pol, lv))
    want = ["%s-%d" % (p, n) for n in range(31001, 31076) for p in ()]
    nums = sorted(int(c.split("-")[1]) for c in ids)
    assert nums == list(range(31001, 31076)), set(range(31001, 31076)) ^ set(nums)
    return 0


if __name__ == "__main__":
    sys.exit(main())

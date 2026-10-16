#!/usr/bin/env python3
"""Builds the 50 b21e cases (v2.1, ids tab-32001..32050).

    cd bench/distill/tools/b21e && python3 build.py
"""
import sys

from common import META, close_sidecar
import s_count, s_group, s_top, s_multi, s_write

MODS = [s_count, s_group, s_top, s_multi, s_write]


def main():
    for m in MODS:
        for b in m.B:
            b()
    close_sidecar()
    ids = sorted(META)
    subs, zh, multi, never, lv = {}, 0, 0, 0, {}
    for c in ids:
        m = META[c]
        subs[m["sub"]] = subs.get(m["sub"], 0) + 1
        zh += m["lang"] == "zh"
        multi += m["turns"] > 1
        never += m["never"]
        lv[m["level"]] = lv.get(m["level"], 0) + 1
    print("cases %d %s zh %d multi %d never_offer %d levels %s" % (len(ids), subs, zh, multi, never, lv))
    nums = sorted(int(c.split("-")[1]) for c in ids)
    assert nums == list(range(32001, 32051)), set(range(32001, 32051)) ^ set(nums)
    return 0


if __name__ == "__main__":
    sys.exit(main())

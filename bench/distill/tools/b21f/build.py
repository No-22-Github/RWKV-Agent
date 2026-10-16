#!/usr/bin/env python3
"""Builds the 50 b21f cases (v2.1, ids log-32101..32150) and replays every bash
reference in the just-bash sidecar.

    cd bench/distill/tools/b21f && python3 build.py
"""
import sys

import common
import m_count
import m_window
import m_top
import m_cross
import m_anom

MODS = [m_count, m_window, m_top, m_cross, m_anom]


def main():
    from common import META, REFS, Sidecar, check_reference
    from lib import run_answers  # noqa: F401
    for m in MODS:
        for b in m.B:
            b()
    sc = Sidecar()
    bad = 0
    import json
    for cid in sorted(REFS):
        files, refs = REFS[cid]
        case = json.load(open(common.BATCH.cases + "/logs/%s/case.json" % cid))
        for i, cmds in enumerate(refs):
            acc = []

            def want(out, root, acc=acc):
                acc.append(out)
            err = None
            for c in cmds:
                err = err or check_reference(sc, files, [c], want)
            out = "\n".join(acc)
            toks = case["turns"][i]["expect"]["output_contains"]
            miss = [t for t in toks if t not in out]
            if err or miss:
                bad += 1
                print(cid, "turn", i + 1, "FAIL", err or "ref output lacks %s: %r" % (miss, out[:300]))
    sc.close()
    ids = sorted(META)
    zh = sum(META[c]["lang"] == "zh" for c in ids)
    multi = sum(META[c]["turns"] > 1 for c in ids)
    subs, lv = {}, {}
    for c in ids:
        subs[META[c]["sub"]] = subs.get(META[c]["sub"], 0) + 1
        lv[META[c]["level"]] = lv.get(META[c]["level"], 0) + 1
    nocalc = sum(bool((META[c]["policy"] or {}).get("never_offer")) for c in ids)
    print("cases %d %s zh %d multi %d nocalc %d levels %s refs-failed %d" % (len(ids), subs, zh, multi, nocalc, lv, bad))
    nums = sorted(int(c.split("-")[1]) for c in ids)
    import os
    if os.environ.get('PARTIAL'):
        return 1 if bad else 0
    assert nums == list(range(32101, 32151)), sorted(set(range(32101, 32151)) ^ set(nums))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

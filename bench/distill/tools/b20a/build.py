#!/usr/bin/env python3
"""Builds the 40 b20a cases (v2.0) and replays every bash reference in the just-bash sidecar.

    cd bench/distill/tools/b20a && python3 build.py [--no-sidecar]
"""
import argparse
import json
import os
import sys

from common import META, REFS, Sidecar, run_reference
import r_delete
import r_move
import r_run
import c_ctl

ORDER = [r_delete, r_move, r_run, c_ctl]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-sidecar", action="store_true")
    args = ap.parse_args()
    for m in ORDER:
        for b in m.BUILDERS:
            b()
    sidecar = None
    if not args.no_sidecar:
        try:
            sidecar = Sidecar()
        except SystemExit as e:
            print("sidecar unavailable: %s" % e)
    bad = 0
    for cid in sorted(REFS):
        if sidecar is None:
            print("%s UNVERIFIED (no sidecar)" % cid)
            bad += 1
            continue
        files, cmds, check = REFS[cid]
        err = run_reference(sidecar, files, cmds, check)
        print("%s %s" % (cid, "ok" if err is None else "FAIL: " + err))
        bad += err is not None
    if sidecar:
        sidecar.close()
    kinds = {}
    for m in META.values():
        kinds[m["kind"]] = kinds.get(m["kind"], 0) + 1
    print("cases %d %s zh %d multi %d refs %d bad %d" % (len(META), kinds, sum(m["lang"] == "zh" for m in META.values()),
          sum(m["turns"] > 1 for m in META.values()), len(REFS), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

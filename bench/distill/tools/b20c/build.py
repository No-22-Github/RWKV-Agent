#!/usr/bin/env python3
"""Builds b20c (v2.0, cases 20081-20140) and replays bash references in the just-bash sidecar.

    cd bench/distill/tools/b20c && python3 build.py [--no-sidecar]
"""
import argparse
import importlib
import json
import os
import sys

from common import META, REFS, Sidecar, run_ref

MODULES = ["a_web", "b_weather", "c_nobash", "d_nodq", "e_nolist", "f_nocalc", "g_nowrite"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-sidecar", action="store_true")
    ap.add_argument("--stats", action="store_true")
    a = ap.parse_args()
    for name in MODULES:
        for b in importlib.import_module(name).BUILDERS:
            b()
    sc = None
    if not a.no_sidecar:
        try:
            sc = Sidecar()
        except SystemExit as e:
            print("sidecar unavailable: %s" % e)
    bad = 0
    for cid in sorted(REFS):
        if sc is None:
            print("%s UNVERIFIED (no sidecar)" % cid)
            continue
        files, cmds, want = REFS[cid]
        err = run_ref(sc, files, cmds, want)
        print("%-10s %s" % (cid, "ok" if err is None else "FAIL " + err[:300]))
        bad += err is not None
    if sc:
        sc.close()
    print("cases %d, bash refs %d, failed %d" % (len(META), len(REFS), bad))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()

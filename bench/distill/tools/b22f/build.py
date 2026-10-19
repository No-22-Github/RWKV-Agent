#!/usr/bin/env python3
"""Builds the 80 b22f cases (v2.2, 8-16K long tasks, ids 34501-34580).

    cd bench/distill/tools/b22f && python3 build.py
"""
import collections
import glob
import importlib
import os
import re
import shutil
import sys

import common

CASES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "v2.2", "cases")
OWN = re.compile(r"^[a-z]+-345(0[1-9]|[1-7][0-9]|80)$")


def clean():
    """Remove only this batch's own case directories (ids 34501-34580), never a scenario directory."""
    for d in glob.glob(os.path.join(CASES, "*", "*-345??")):
        if OWN.match(os.path.basename(d)) and os.path.isdir(d):
            shutil.rmtree(d)

MODS = ["f1a", "f1b", "f1c", "f1d", "f1e", "f2a", "f2b", "f2c", "f2d", "f3a", "f3b", "f4a", "f4b", "f4c"]


def main():
    clean()
    for name in MODS:
        try:
            m = importlib.import_module(name)
        except ModuleNotFoundError as e:
            if e.name != name:
                raise
            continue
        m.build()
    ids = sorted(common.META)
    subs = collections.Counter(common.META[c]["sub"] for c in ids)
    zh = sum(common.META[c]["zh"] for c in ids)
    multi = sum(common.META[c]["turns"] > 1 for c in ids)
    ests = [common.META[c]["est"] for c in ids]
    print("cases %d %s zh %d multi %d est min %d max %d" % (len(ids), dict(subs), zh, multi, min(ests) if ests else 0, max(ests) if ests else 0))
    return 0


if __name__ == "__main__":
    sys.exit(main())

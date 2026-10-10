#!/usr/bin/env python3
"""Builds the v1.41 b12 pilot cases and checks every bash reference solution
in the just-bash sidecar.

    cd bench/distill/tools/v1.41/b12_build && python3 build.py
"""
import sys

import m9a
import m9b
import m10
import m10b
from common import Sidecar, check_reference

MODULES = [m9a, m9b, m10, m10b]


def main():
    sidecar = Sidecar()
    failures = 0
    for module in MODULES:
        for builder in module.BUILDERS:
            path = builder()
            cid = path.rsplit("/", 1)[-1]
            ref = getattr(module, "REFS", {}).get(cid)
            if ref is None:
                print(f"{cid:10s} written (no bash reference)")
                continue
            files, commands, want = ref
            error = check_reference(sidecar, files, commands, want)
            print(f"{cid:10s} {'ok' if error is None else 'FAIL: ' + error}")
            failures += error is not None
    sidecar.close()
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()

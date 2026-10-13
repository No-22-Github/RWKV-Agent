#!/usr/bin/env python3
"""Builds the v1.42 b14 cases and replays every bash reference solution in the
just-bash sidecar (local/bin/justbash-sidecar, from scripts/build-justbash.sh).

    cd bench/distill/tools/b14 && python3 build.py [--no-sidecar] [--only m9agg,...] [--report out.json]

Without the sidecar (or with --no-sidecar) the cases are still written and
every bash case is reported as unverified, never as passed.
"""
import argparse
import importlib
import json
import os
import sys

from common import META, REFS, SPEC, Sidecar, run_reference, thousands

MODULES = ["m9agg", "m9exact", "m9edit", "m9recover", "m9neg", "m10w"]


def answer_check(answer):
    forms = thousands(answer) if answer.replace(".", "", 1).isdigit() else [answer]

    def check(out, _read):
        return None if any(f in out for f in forms) else "ref stdout %r lacks %s" % (out[-300:], forms)
    return check


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-sidecar", action="store_true")
    ap.add_argument("--only", default="")
    ap.add_argument("--report", default="")
    ap.add_argument("--ids", default="", help="comma-separated case ids to rebuild")
    args = ap.parse_args()
    names = [m for m in MODULES if not args.only or m in args.only.split(",")]
    sidecar = None
    if not args.no_sidecar:
        try:
            sidecar = Sidecar()
        except SystemExit as e:
            print("sidecar unavailable: %s" % e)
    results = {}
    for name in names:
        try:
            module = importlib.import_module(name)
        except ModuleNotFoundError as e:
            if e.name == name:
                continue
            raise
        for builder in module.BUILDERS:
            if args.ids and builder.__name__.replace("_", "-") not in args.ids.split(","):
                continue
            path = builder()
            cid = os.path.basename(path)
            ref = REFS.get(cid)
            if ref is None:
                results[cid] = "no bash reference"
                continue
            if sidecar is None:
                results[cid] = "UNVERIFIED (no sidecar)"
                continue
            files, commands, want = ref
            if isinstance(want, list):  # one answer per turn, one command per turn
                errors = [run_reference(sidecar, files, [c], answer_check(a)) for c, a in zip(commands, want)]
                error = "; ".join(e for e in errors if e) or None
            else:
                error = run_reference(sidecar, files, commands, want)
            results[cid] = "ok" if error is None else "FAIL: " + error
            print("%-11s %s" % (cid, results[cid][:400]), flush=True)
    if sidecar:
        sidecar.close()
    bad = {k: v for k, v in results.items() if v.startswith(("FAIL", "UNVERIFIED"))}
    print("cases %d, bash refs ok %d, failed/unverified %d, no bash ref %d" % (
        len(results), sum(v == "ok" for v in results.values()), len(bad), sum(v == "no bash reference" for v in results.values())))
    if not args.only and not args.ids:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "specs.json"), "w", encoding="utf-8") as f:
            json.dump(SPEC, f, ensure_ascii=False, indent=1, sort_keys=True)
            f.write("\n")
    if args.report:
        with open(args.report, "w") as f:
            json.dump({"results": results, "meta": META, "spec": SPEC}, f, ensure_ascii=False, indent=1, sort_keys=True)
            f.write("\n")
    sys.exit(1 if any(v.startswith("FAIL") for v in results.values()) else 0)


if __name__ == "__main__":
    main()

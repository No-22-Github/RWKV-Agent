#!/usr/bin/env python3
"""Drops `corpus paths` output whose source runs are all behavior rejects.

    python3 filter_paths.py --paths raw.jsonl --out kept.jsonl --runs <run-dir> [<run-dir> ...]

A path is matched to the runs that passed the case with the same final answers;
it is kept when at least one of them is covered or ordinary (behavior.py labels)
and dropped when every matching run is a reject. Prints the kept count per
sub-class and label. S5 reading exclusions are separate (common/exclude.jsonl).
"""
import argparse
import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import behavior  # noqa: E402


def finals(turns):
    return [((t.get("result") or {}).get("output") or "").strip() for t in turns]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--paths", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--runs", nargs="+", required=True)
    args = ap.parse_args()
    runs = []
    for run_dir in args.runs:
        cases = {c["id"]: c for c in json.load(open(os.path.join(run_dir, "summary.json")))["cases"]}
        labels = {cid: (passed, behavior.label(cid, passed, steps, dropped)[0])
                  for cid, passed, steps, dropped in behavior.load_runs(run_dir)}
        runs.append((cases, labels))
    kept, dropped, tally = [], [], collections.Counter()
    for line in open(args.paths):
        d = json.loads(line)
        cid = d["case_id"].split("--")[0]
        want = [o["text"].strip() for o in d["outputs"] if not o["text"].startswith("<tool_call>")]
        found = []
        for cases, labels in runs:
            c = cases.get(cid)
            if c and c.get("passed") and finals(c["turns"]) == want:
                found.append(labels[cid][1])
        if "covered" in found or "ordinary" in found:
            kept.append(line)
            tally[(behavior.SPEC.get(cid, {}).get("sub", "?"), "covered" if "covered" in found else "ordinary")] += 1
        else:
            dropped.append((d["case_id"], found))
    with open(args.out, "w") as f:
        f.writelines(kept)
    print("kept", len(kept), "dropped", len(dropped))
    for x in dropped:
        print("  dropped", x[0], x[1])
    for key in sorted(tally):
        print("  %s %s %d" % (key[0], key[1], tally[key]))


if __name__ == "__main__":
    main()

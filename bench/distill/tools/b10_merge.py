#!/usr/bin/env python3
"""Merge step.py solve rounds into one b10 replay script.

  b10_merge.py --round <solve_dir>[:<case,case,...>] ... --out <script.jsonl> [--suffix --p101]

Rounds are given oldest first. A round with a case list contributes only those
cases; a later round overrides an earlier one for the same case. Unlike
collect.py, failed states are kept: when a case was fixed after the solve
(version bump for a criterion defect, distill-workflow S5 ①), the old path is
re-scored by `corpus render` against the current case, and render rejects it if
it still fails. Zero-call discipline is checked here, as in collect.py.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from collect import LOOK_FIRST_TASKS, split_turns  # noqa: E402
from distill_paths import find_case  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", action="append", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--suffix", default="--p101")
    args = ap.parse_args()
    chosen = {}
    for spec in args.round:
        path, _, only = spec.partition(":")
        wanted = set(only.split(",")) if only else None
        for name in sorted(os.listdir(path)):
            if not name.endswith(".json"):
                continue
            st = json.load(open(os.path.join(path, name)))
            if st["status"] == "open" or (wanted is not None and st["case_id"] not in wanted):
                continue
            chosen[st["case_id"]] = (st, path)
    entries, rejected = [], []
    for cid in sorted(chosen):
        st, src = chosen[cid]
        case = find_case(cid)
        turns = split_turns(st["outputs"], len(case["turns"])) if case else None
        if turns is None:
            rejected.append((cid, "cannot split outputs into turns"))
            continue
        task = case["tags"]["task_type"]
        bad = [i + 1 for i, (t, spec) in enumerate(zip(turns, case["turns"]))
               if ((case["tags"]["scenario"] == "notool" and task not in LOOK_FIRST_TASKS
                    and spec["expect"].get("tools") == [])
                   or spec["expect"].get("require_active_no_call"))
               and any("<tool_call>" in o for o in t)]
        if bad:
            rejected.append((cid, "tool call on zero-call turn %s" % bad))
            continue
        entries.append({"case_id": cid + args.suffix,
                        "outputs": [{"text": t, "supervised": True} for t in st["outputs"]]})
        print("%s\t%s\t%s" % (cid, st["status"], os.path.basename(src.rstrip("/"))))
    with open(args.out, "w") as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    print("written: %d entries -> %s" % (len(entries), args.out))
    for cid, why in rejected:
        print("REJECT %s: %s" % (cid, why))


if __name__ == "__main__":
    main()

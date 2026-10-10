#!/usr/bin/env python3
"""Collect solved b04 cases (step.py state files) into a replay script.

  collect.py [--solve local/runs/distill/b04/solve] [--out bench/distill/v1/teacher/b04.jsonl]
             [--suffix --p41]

Only "pass" cases are written. Entry IDs are "<case id><suffix>", suffix
defaulting to --p41: b01-b03 already use --p1/--p2 for the same bank cases,
and exclude.jsonl removes by entry ID, so a shared suffix would let one
exclusion delete another batch's path.

Zero-call discipline is enforced here, not by the scorer: expect.tools == []
is diagnostic only in scorer v3, and the 2026-09-26 audit found 387 rows on
tools:[] cases that still called tools. A turn must have no <tool_call> when
the turn declares tools: [] in a notool case other than LOOK_FIRST_TASKS, or
the turn has require_active_no_call. The rule is per turn: old ambiguous_request
cases ask blind on turn 1 (tools: []) and read the workspace on turn 2 (no
tools key); b04 W0 first applied it per case and failed all 25 of them. Refusals may look first (distill-workflow §4.3.1);
stable_fact cases in this bank were drafted with the answer in a workspace file
(audit P1), so they are tool cases in practice.
"""
import argparse
import collections
import glob
import json
import os

from distill_paths import REPO, find_case, teacher_script

LOOK_FIRST_TASKS = {"beyond_capability", "stable_fact"}


def split_turns(outputs, n_turns):
    """Outputs per turn: a turn ends at its first non-tool output."""
    turns, cur = [], []
    for text in outputs:
        cur.append(text)
        if "<tool_call>" not in text:
            turns.append(cur)
            cur = []
    if cur:
        turns.append(cur)
    return turns if len(turns) == n_turns else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solve", default=os.path.join(REPO, "local", "runs", "distill", "b04", "solve"))
    ap.add_argument("--out", default=teacher_script("v1", "b04"))
    ap.add_argument("--suffix", default="--p41")
    args = ap.parse_args()
    counts = collections.Counter()
    rejected = []
    entries = []
    for path in sorted(glob.glob(os.path.join(args.solve, "*.json"))):
        state = json.load(open(path))
        cid = state["case_id"]
        counts["status:" + state["status"]] += 1
        if state["status"] != "pass":
            continue
        case = find_case(cid)
        if case is None:
            rejected.append((cid, "case not found under bench/distill/*/cases"))
            continue
        turns = split_turns(state["outputs"], len(case["turns"]))
        if turns is None:
            rejected.append((cid, "cannot split outputs into %d turns" % len(case["turns"])))
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
        counts["scenario:" + case["tags"]["scenario"]] += 1
        counts["task:" + task] += 1
        entries.append({"case_id": cid + args.suffix,
                        "outputs": [{"text": t, "supervised": True} for t in state["outputs"]]})
    tmp = args.out + ".tmp"
    with open(tmp, "w") as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    os.replace(tmp, args.out)
    for k in sorted(counts):
        print("%-32s %d" % (k, counts[k]))
    print("written: %d entries -> %s" % (len(entries), os.path.relpath(args.out, REPO)))
    for cid, why in rejected:
        print("REJECT %s: %s" % (cid, why))


if __name__ == "__main__":
    main()

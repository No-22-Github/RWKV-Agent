#!/usr/bin/env python3
"""Mechanical checks on solved b10 paths (v1.4 §3–§4) before they go to render.

  b10_check.py [--solve local/runs/distill/v14/b10-pilot/solve] [--report <tsv>]

The scorer already enforces the per-case expectations; this adds the
path-shape rules the scorer cannot see:

  write_readback   every write is followed later by a read of the same path (§3.5)
  final_shape      last output of each turn: no tool call / role label / ✿ / markdown,
                   not bare UNKNOWN, <= 600 chars (§4.2)
  done_line        a final that says DONE puts it on its own last line (§4.1)
  whole_read       a case with max_calls.read_file == 1 (M6) read an 80+ line table or log whole (§3.6, §7.7)

It also prints the opening-word distribution of final answers so a templated
batch shows up as one dominant opening.
"""
import argparse
import collections
import glob
import json
import os
import re

from distill_paths import REPO, find_case
WRITE_TOOLS = {"write_file", "replace_lines", "append_file"}
READ_TOOLS = {"read_file", "read_lines"}


def call_of(text):
    m = re.fullmatch(r"<tool_call>(.*)</tool_call>", text.strip(), re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return {"name": "?", "arguments": {}}


def finals(outputs):
    return [o for o in outputs if call_of(o) is None]


def check(state, case):
    problems = []
    outs = state["outputs"]
    calls = [c for c in (call_of(o) for o in outs) if c]
    for i, c in enumerate(calls):
        if c["name"] in WRITE_TOOLS:
            path = c["arguments"].get("path")
            if not any(d["name"] in READ_TOOLS and d["arguments"].get("path") == path for d in calls[i + 1:]):
                problems.append("write_readback: no read of %s after %s" % (path, c["name"]))
    for f in finals(outs):
        if re.search(r"<tool_call>|<tool_response>|✿|^(User|Assistant):", f, re.M):
            problems.append("final_shape: protocol text in final")
        if re.search(r"^\s*#|\*\*|^\s*\|.*\|\s*$", f, re.M):
            problems.append("final_shape: markdown in final")
        if f.strip() in ("UNKNOWN", "不知道", "unknown"):
            problems.append("final_shape: bare UNKNOWN")
        if len(f) > 600:
            problems.append("final_shape: %d chars" % len(f))
        if "DONE" in f and f.strip().splitlines()[-1].strip() != "DONE":
            problems.append("done_line: DONE not on its own last line")
    big = [p for p, t in case.get("files", {}).items() if p.endswith((".csv", ".jsonl", ".log")) and t.count("\n") >= 80]
    if case.get("expect", {}).get("max_calls", {}).get("read_file") == 1:
        for c in calls:
            if c["name"] == "read_file" and c["arguments"].get("path") in big:
                problems.append("whole_read: read_file on %s" % c["arguments"]["path"])
    return problems


def opening(text):
    t = text.strip()
    m = re.match(r"[A-Za-z]+(?:\s+[A-Za-z]+)?", t)
    return m.group(0) if m else t[:3]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solve", default=os.path.join(REPO, "local", "runs", "distill", "v14", "b10-pilot", "solve"))
    ap.add_argument("--report")
    args = ap.parse_args()
    rows, opens = [], collections.Counter()
    for path in sorted(glob.glob(os.path.join(args.solve, "*.json"))):
        st = json.load(open(path))
        case = find_case(st["case_id"])
        probs = check(st, case) if case else ["case not found"]
        if st["status"] == "pass":
            for f in finals(st["outputs"]):
                opens[opening(f)] += 1
        rows.append((st["case_id"], st["status"], len(st["outputs"]), "; ".join(probs)))
    for r in rows:
        print("%s\t%s\t%d\t%s" % r)
    print("\nopenings of PASS finals (top 12):")
    for k, v in opens.most_common(12):
        print("  %3d  %s" % (v, k))
    if args.report:
        with open(args.report, "w") as f:
            for r in rows:
                f.write("%s\t%s\t%d\t%s\n" % r)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Per-case failure taxonomy across bench arms (v1.2 trace review, 2026-09-30).

usage: classify_failures.py <runs_root> [--suite workbank|bfclp] [--arms a,b,...]

<runs_root> holds one directory per arm, laid out as local/runs/bench-v12/:
<arm>/<arm>-<suite>-g1k-agent-k0/summary.json. workbank is scored on the clean
112 (bench/workbank/seeded-base700.txt excluded). Each case lands in exactly
one class; the first matching rule wins, in the order below.

  PASS                    passed under the scorer that wrote summary.json
  closeout_tool_call      tool call emitted in the answer stage (after a
                          duplicate rejection): the run's dominant failure
  bad_tool_json           tool call JSON undecodable or of the wrong shape
  think_block             unclosed or stray <think> block
  protocol_other          any other runner protocol error
  degenerate_loop         final output compresses below 12% (":"":"":... loops)
  envelope_leak_in_final  tool envelope, fake tool result or role label in the answer
  fabricated_tool         called a tool the turn never offered
  zero_call_direct        tool task answered without a single tool call
  unknown                 answered UNKNOWN after calling tools
  verbose_or_refuse       numeric task answered in prose or refused
  wrong_answer            everything else
"""
import argparse
import glob
import os
import re
import zlib
from collections import Counter
import json

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
NO_CALL_CATEGORIES = {"notool", "bfcl-irrelevance", "bfcl-missing-required"}


def seeded_ids():
    path = os.path.join(REPO, "bench", "workbank", "seeded-base700.txt")
    return {l.strip() for l in open(path) if l.strip() and not l.startswith("#")}


def degenerate(text):
    raw = text.encode()
    return len(raw) >= 200 and len(zlib.compress(raw)) / len(raw) < 0.12


def leaked(text):
    return bool(re.search(r'<tool_call>|"arguments"\s*:|tool_call_id|Toolcall|^\s*\{"ok"|^Assistant:|✿', text))


def classify(case):
    steps = [s for t in case["turns"] for s in t.get("result", {}).get("steps", [])]
    calls = [s for s in steps if s.get("action_type") == "tool" and s.get("tool")]
    output = case["turns"][-1].get("result", {}).get("output", "") or ""
    failures = " ".join(f for t in case["turns"] for f in t.get("failures", []))
    if case["passed"]:
        return "PASS"
    if "runner error" in failures:
        if "forbidden during answer" in failures:
            return "closeout_tool_call"
        if "JSON decode" in failures or "shape" in failures:
            return "bad_tool_json"
        if "think" in failures:
            return "think_block"
        return "protocol_other"
    if degenerate(output):
        return "degenerate_loop"
    if leaked(output):
        return "envelope_leak_in_final"
    if any(s.get("tool_rejected_reason") == "unknown_tool" for s in steps):
        return "fabricated_tool"
    if not calls and case["category"] not in NO_CALL_CATEGORIES:
        return "zero_call_direct"
    if output.strip().upper().startswith("UNKNOWN"):
        return "unknown"
    if "plain number" in failures:
        return "verbose_or_refuse"
    return "wrong_answer"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("runs_root")
    parser.add_argument("--suite", default="workbank", choices=["workbank", "bfclp"])
    parser.add_argument("--arms", help="comma-separated arm names (default: every arm under runs_root)")
    args = parser.parse_args()
    arms = args.arms.split(",") if args.arms else sorted(
        d for d in os.listdir(args.runs_root) if os.path.isdir(os.path.join(args.runs_root, d)))
    seeded = seeded_ids() if args.suite == "workbank" else set()
    table = {}
    for arm in arms:
        found = glob.glob(os.path.join(args.runs_root, arm, f"{arm}-{args.suite}-*", "summary.json"))
        if not found:
            continue
        cases = [c for c in json.load(open(found[0]))["cases"] if c["id"] not in seeded]
        table[arm] = Counter(classify(c) for c in cases)
    classes = sorted({k for v in table.values() for k in v}, key=lambda k: -sum(v[k] for v in table.values()))
    print("%-24s" % "class" + "".join("%11s" % a[-10:] for a in table))
    for cls in classes:
        print("%-24s" % cls + "".join("%11d" % table[a][cls] for a in table))


if __name__ == "__main__":
    main()

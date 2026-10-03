#!/usr/bin/env python3
"""Per-case failure taxonomy across bench arms (v1.2 trace review, 2026-09-30).

usage: classify_failures.py <runs_root> [--suite workbank|bfclp] [--arms a,b,...]

<runs_root> holds either flat run directories or nested arm directories:
  flat:   <runs_root>/<run-name>-<suite>-*/summary.json
  nested: <runs_root>/<arm>/<arm>-<suite>-*/summary.json
  single: <runs_root>/summary.json

workbank is scored on the clean 112 (bench/workbank/seeded-base700.txt excluded).
Each case lands in exactly one class; the first matching rule wins, in the order below.

  PASS                    passed under the scorer that wrote summary.json
  closeout_tool_call      tool call emitted in the answer stage (after a duplicate rejection)
  bad_tool_json           tool call JSON undecodable or of the wrong shape
  think_block             unclosed or stray <think> block
  protocol_other          any other runner protocol error
  degenerate_loop         final output compresses below 12% (":"":"":... loops)
  envelope_leak_in_final  tool envelope, fake tool result or role label in the answer
  fabricated_tool         called a tool the turn never offered
  zero_call_direct        tool task answered without a single tool call
  unknown                 answered UNKNOWN after calling tools
  short_garbage           final output <=20 chars, not pure number/ID, not UNKNOWN/DONE
  verbose_or_refuse       numeric task answered in prose or refused
  wrong_answer            everything else
"""
import argparse
import glob
import json
import os
import re
import zlib
from collections import Counter

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
NO_CALL_CATEGORIES = {"notool", "bfcl-irrelevance", "bfcl-missing-required"}


def seeded_ids():
    path = os.path.join(REPO, "bench", "workbank", "seeded-base700.txt")
    if not os.path.exists(path):
        return set()
    return {l.strip() for l in open(path) if l.strip() and not l.startswith("#")}


def degenerate(text):
    raw = text.encode()
    return len(raw) >= 200 and len(zlib.compress(raw)) / len(raw) < 0.12


def leaked(text):
    return bool(re.search(r'<tool_call>|"arguments"\s*:|tool_call_id|Toolcall|^\s*\{"ok"|^Assistant:|✿', text))


def is_pure_number(s):
    try:
        float(s.replace(',', ''))
        return True
    except ValueError:
        return False


def is_short_garbage(output, failures=""):
    s = output.strip()
    if not s or len(s) > 20:
        return False
    u = s.upper()
    if u == "DONE" or u.startswith("UNKNOWN"):
        return False
    if is_pure_number(s):
        return False
    # entity code / uppercase identifier with digits like MRA-2088
    if re.match(r'^[A-Z0-9_-]+$', s) and not re.match(r'^[A-Z]+$', s):
        return False
    return True


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
    if not calls and case.get("category", "") not in NO_CALL_CATEGORIES:
        return "zero_call_direct"
    if output.strip().upper().startswith("UNKNOWN"):
        return "unknown"
    if is_short_garbage(output, failures):
        return "short_garbage"
    if "plain number" in failures:
        return "verbose_or_refuse"
    return "wrong_answer"


def find_summaries(runs_root, suite, arms=None):
    """Locate summary.json files supporting flat, nested, and direct paths."""
    results = {}
    if os.path.isfile(runs_root) and runs_root.endswith(".json"):
        results[os.path.basename(os.path.dirname(runs_root))] = runs_root
        return results

    if os.path.isfile(os.path.join(runs_root, "summary.json")):
        results[os.path.basename(runs_root)] = os.path.join(runs_root, "summary.json")
        return results

    filter_arms = arms.split(",") if arms else None

    # Check flat layout: runs_root/<dir-with-suite>/summary.json
    pattern = f"*-{suite}-*"
    candidate_dirs = [d for d in sorted(glob.glob(os.path.join(runs_root, pattern))) if os.path.isdir(d)]
    if candidate_dirs:
        for d in candidate_dirs:
            base = os.path.basename(d)
            summary_path = os.path.join(d, "summary.json")
            if not os.path.exists(summary_path):
                continue
            if filter_arms:
                matched = any(base == fa or base.startswith(fa + "-") or base.startswith(fa + "_") or fa in base for fa in filter_arms)
                if not matched:
                    continue
            results[base] = summary_path
        return results

    # Check nested layout: runs_root/<arm>/<arm>-<suite>-*/summary.json
    subdirs = sorted(d for d in os.listdir(runs_root) if os.path.isdir(os.path.join(runs_root, d)))
    if filter_arms:
        subdirs = [d for d in subdirs if d in filter_arms or any(fa in d for fa in filter_arms)]
    for arm in subdirs:
        found = glob.glob(os.path.join(runs_root, arm, f"{arm}-{suite}-*", "summary.json"))
        if not found:
            found = glob.glob(os.path.join(runs_root, arm, f"*-{suite}-*", "summary.json"))
        if found:
            results[arm] = found[0]

    return results


def main():
    parser = argparse.ArgumentParser(description="Classify failure modes from bench runs.")
    parser.add_argument("runs_root", help="Path to runs directory or summary.json")
    parser.add_argument("--suite", default="workbank", help="Suite name (workbank, bfclp, etc.)")
    parser.add_argument("--arms", help="Comma-separated arm names to filter")
    args = parser.parse_args()

    summaries = find_summaries(args.runs_root, args.suite, args.arms)
    if not summaries:
        print(f"No summary.json found under {args.runs_root} for suite={args.suite}")
        return

    seeded = seeded_ids() if args.suite == "workbank" else set()
    table = {}
    for name, path in summaries.items():
        try:
            with open(path) as f:
                data = json.load(f)
        except Exception as e:
            print(f"Failed to load {path}: {e}")
            continue
        cases = [c for c in data.get("cases", []) if c.get("id") not in seeded]
        table[name] = Counter(classify(c) for c in cases)

    classes = [
        "PASS",
        "closeout_tool_call",
        "bad_tool_json",
        "think_block",
        "protocol_other",
        "degenerate_loop",
        "envelope_leak_in_final",
        "fabricated_tool",
        "zero_call_direct",
        "unknown",
        "short_garbage",
        "verbose_or_refuse",
        "wrong_answer",
    ]
    # Filter to classes that appeared in at least one arm
    active_classes = [cls for cls in classes if any(table[a][cls] > 0 for a in table)]

    col_names = list(table.keys())
    # Format header
    col_width = max(16, max((len(c) for c in col_names), default=16) + 2)
    header = "%-24s" % "class" + "".join(f"%{col_width}s" % a for a in col_names)
    print(header)
    print("-" * len(header))
    for cls in active_classes:
        row = "%-24s" % cls + "".join(f"%{col_width}d" % table[a][cls] for a in col_names)
        print(row)


if __name__ == "__main__":
    main()

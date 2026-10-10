#!/usr/bin/env python3
"""Cut the UNKNOWN clause from two thirds of the distill cases (v1.3 §3.3).

  v13_edit_contracts.py [--scan bench/distill/tools/v1.3/scan-v12.json] [--apply]

Dry run by default. Every bench/distill case whose last-turn prompt ends with
the full answer contract gets a fate by case-ID hash:

  1/3 full        prompt untouched; tags.answer_style = "unknown"
  2/3 value_only  " If you cannot determine the answer, reply exactly UNKNOWN."
                  is cut, "Reply with only the final answer." stays;
                  tags.answer_style = "value"; tags.version += 1

The 25 absent cases listed in the scan are skipped: they need a hand edit of
prompt and expect (§3.2). Old replay scripts still pass a value_only case: the
answer is unchanged, only the abstention clause is gone.
"""
import argparse
import glob
import hashlib
import json
import os

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
FULL = "Reply with only the final answer. If you cannot determine the answer, reply exactly UNKNOWN."
VALUE = "Reply with only the final answer."
DUMPS = [dict(indent=2, ensure_ascii=False), dict(indent=2)]


def fate(case_id):
    return "full" if int(hashlib.sha256(case_id.encode()).hexdigest(), 16) % 3 == 0 else "value_only"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", default=os.path.join(REPO, "bench", "distill", "tools", "v1.3", "scan-v12.json"))
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    absent = set(json.load(open(args.scan))["fix"]["absent_cases"])
    counts = {"value_only": 0, "full": 0, "absent_skipped": 0, "no_contract": 0}
    reformatted = []
    for path in sorted(glob.glob(os.path.join(REPO, "bench", "distill", "cases", "*", "*", "*", "case.json"))):
        raw = open(path).read()
        case = json.loads(raw)
        last = case["turns"][-1]
        if not last["prompt"].endswith(FULL):
            counts["no_contract"] += 1
            continue
        if case["id"] in absent:
            counts["absent_skipped"] += 1
            continue
        style = next((kw for kw in DUMPS if json.dumps(case, **kw) + "\n" == raw), None)
        verdict = fate(case["id"])
        if verdict == "value_only":
            last["prompt"] = last["prompt"][: -len(FULL)] + VALUE
            case["tags"]["version"] = case["tags"].get("version", 1) + 1
            case["tags"]["answer_style"] = "value"
        else:
            case["tags"]["answer_style"] = "unknown"
        counts[verdict] += 1
        if style is None:
            # Only the hand-written sample tab-5001: normalising it is a whitespace-only diff.
            reformatted.append(os.path.relpath(path, REPO))
            style = DUMPS[0]
        if args.apply:
            with open(path, "w") as f:
                f.write(json.dumps(case, **style) + "\n")
    print(("applied" if args.apply else "dry run"), counts)
    for path in reformatted:
        print("reformatted (whitespace only):", path)


if __name__ == "__main__":
    main()

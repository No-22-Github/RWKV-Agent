#!/usr/bin/env python3
"""coverage.py — scenario x level fill status for the workbank bank.

Reads quotas (and the per-scenario level mix) from docs/tag-vocab.json,
counts the cases filled under --cases, and reports the gap table. The level
mix is 15/40/30/15 with a tolerance of +/-1 case per level per scenario
(HANDOFF.md section 6).

  --summary   print the full fill table
  --gaps      print only the gaps (levels below quota-1 or above quota+1)

Exit code is always 0: this is a planning tool, lint.py is the gate.
Standard library only.
"""

import argparse
import json
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
WORKBANK_DIR = TOOLS_DIR.parent
DEFAULT_CASES = WORKBANK_DIR / "cases"
DEFAULT_VOCAB = WORKBANK_DIR / "docs" / "tag-vocab.json"
TOLERANCE = 1


def expected_counts(quota, mix):
    """Largest-remainder split of a scenario quota across L0..L3."""
    raw = {level: quota * share for level, share in mix.items()}
    base = {level: int(x // 1) for level, x in raw.items()}
    order = sorted(raw, key=lambda level: (raw[level] - base[level]), reverse=True)
    short = quota - sum(base.values())
    for i in range(max(short, 0)):
        base[order[i % len(order)]] += 1
    return base


def load_cases(root):
    cells = {}
    for path in sorted(Path(root).rglob("case.json")):
        try:
            with open(path, encoding="utf-8") as fh:
                case = json.load(fh)
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        tags = case.get("tags") or {}
        scenario, level = tags.get("scenario"), tags.get("level")
        if isinstance(scenario, str) and isinstance(level, str):
            cells[(scenario, level)] = cells.get((scenario, level), 0) + 1
    return cells


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Report scenario x level coverage of the workbank case tree against the quotas.")
    parser.add_argument("--cases", default=str(DEFAULT_CASES),
                        help=f"cases root directory (default: {DEFAULT_CASES})")
    parser.add_argument("--vocab", default=str(DEFAULT_VOCAB),
                        help=f"tag vocabulary file with quotas (default: {DEFAULT_VOCAB})")
    parser.add_argument("--gaps", action="store_true", help="print only the gaps")
    parser.add_argument("--summary", action="store_true", help="print the full fill table")
    args = parser.parse_args(argv)

    with open(args.vocab, encoding="utf-8") as fh:
        vocab = json.load(fh)
    scenarios = vocab["scenarios"]
    mix = vocab["level_mix"]
    levels = vocab["levels"]
    cells = load_cases(args.cases)

    show_all = args.summary or not args.gaps
    show_gaps = args.gaps or not args.summary

    gap_lines = []
    total = 0
    for entry in scenarios:
        name, quota = entry["name"], entry["quota"]
        want = expected_counts(quota, mix)
        have = {level: cells.get((name, level), 0) for level in levels}
        filled = sum(have.values())
        total += filled
        if show_all:
            row = "  ".join(f"{level} {have[level]:>2}/{want[level]:<2}" for level in levels)
            print(f"{name:<10} ({quota:>3} slots, filled {filled:>3}): {row}")
        for level in levels:
            delta = have[level] - want[level]
            if delta < -TOLERANCE:
                gap_lines.append(f"  {name:<10} {level}: need {want[level]}, have {have[level]} (short {-delta})")
            elif delta > TOLERANCE:
                gap_lines.append(f"  {name:<10} {level}: quota {want[level]}, have {have[level]} (over by {delta})")

    if show_gaps:
        if gap_lines:
            print(f"gaps ({len(gap_lines)}):")
            for line in gap_lines:
                print(line)
        else:
            print("no gaps: every scenario is within +/-1 of its level mix")
    print(f"total cases filled: {total}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

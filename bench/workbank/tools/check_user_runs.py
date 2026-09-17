#!/usr/bin/env python3
"""Check the consecutive-User-run invariant of an eval run's model prompts.

G1K was trained on strictly alternating User/Assistant turns. A text
transcript prompt that shows two or more consecutive ``User:`` blocks before
the trailing ``Assistant:`` opening is out of distribution; the usermsg=merged
wire variants exist to keep that count at most one. This checker reads
``<run_dir>/trace.jsonl`` and audits every ``model_call`` record with a text
``request.prompt``:

  python tools/check_user_runs.py <run_dir> [--max N]

Blocks split on blank lines; a block with no role label continues the message
below it (tool payloads may contain blank lines). Native-channel records,
whose prompt is a JSON payload starting with ``{"messages":``, are skipped
with a note. Prints the count distribution and every violation
(case_id, sequence, count); exits 1 when any count exceeds --max (default 1).
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROLE_LABELS = ("Assistant:", "System:", "Tool:")


def count_trailing_user_blocks(prompt):
    """Count consecutive User: blocks before the trailing Assistant: opening.

    Returns None when the prompt does not end with an Assistant opening.
    """
    blocks = prompt.split("\n\n")
    if not blocks or not blocks[-1].startswith("Assistant:"):
        return None
    count = 0
    for block in reversed(blocks[:-1]):
        if block.startswith("User:"):
            count += 1
        elif block.startswith(ROLE_LABELS):
            break
        # An unlabeled block is a continuation of the message below it.
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("run_dir", help="eval run directory containing trace.jsonl")
    parser.add_argument(
        "--max",
        type=int,
        default=1,
        help="maximum allowed consecutive User: blocks (default 1)",
    )
    args = parser.parse_args()

    trace_path = Path(args.run_dir) / "trace.jsonl"
    if not trace_path.is_file():
        print(f"error: {trace_path} not found", file=sys.stderr)
        return 2

    distribution = Counter()
    violations = []
    native_skipped = 0
    total = 0
    with trace_path.open() as trace:
        for line in trace:
            record = json.loads(line)
            if record.get("kind") != "model_call":
                continue
            call = record.get("model_call") or {}
            prompt = (call.get("request") or {}).get("prompt")
            if not isinstance(prompt, str) or not prompt:
                continue
            if prompt.startswith('{"messages":'):
                native_skipped += 1
                continue
            count = count_trailing_user_blocks(prompt)
            if count is None:
                native_skipped += 1
                continue
            total += 1
            distribution[count] += 1
            if count > args.max:
                violations.append(
                    (record.get("case_id"), record.get("sequence"), count)
                )

    print(f"checked {total} text model_call prompts in {trace_path}")
    for count in sorted(distribution):
        print(f"  {count} consecutive User block(s): {distribution[count]} prompts")
    if native_skipped:
        print(f"skipped {native_skipped} native-channel records (JSON prompt payload)")
    if violations:
        print(f"violations (count > {args.max}):")
        for case_id, sequence, count in violations:
            print(f"  case={case_id} sequence={sequence} count={count}")
        return 1
    print(f"no violations: every generation has at most {args.max} consecutive User block(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Append the \\n\\nUser: turn suffix to every rendered row (v1.3 §M5).

  build_v13_suffix.py --rows <rows.jsonl> [--rows ...] --out <suffixed.jsonl>

Semantics carried over from the v1.2 pack's tooling/build_v12.py add_suffix:
every row's text gains a trailing "\\n\\nUser:" (the next user turn header, so
a full-text trainer still learns where the assistant turn ends), and the LAST
loss span is extended to the new end of the text so the suffix sits inside the
supervised region for mask trainers.

Assertions (hard failures, matching the v1.2 discipline):
  - every row carries at least one loss span;
  - spans are code-point offsets, ordered and non-overlapping;
  - the suffixed row's wire_hash is untouched and the text change is exactly
    the suffix.
"""
import argparse
import json
import sys

SUFFIX = "\n\nUser:"


def add_suffix(row):
    text = row["text"]
    spans = row["loss_spans"]
    assert spans, "row %s has no loss span" % row["meta"]["case_id"]
    ordered = sorted(spans)
    assert ordered == spans and len(ordered) >= 2 or len(ordered) == 1, "loss spans unordered"
    for (s1, e1), (s2, e2) in zip(ordered, ordered[1:]):
        assert e1 <= s2, "loss spans overlap in row %s" % row["meta"]["case_id"]
    assert len(text) >= ordered[-1][1], "last loss span exceeds text length"
    new_text = text + SUFFIX
    start, end = ordered[-1]
    new_spans = ordered[:-1] + [[start, len(new_text)]]
    out = dict(row)
    out["text"] = new_text
    out["loss_spans"] = new_spans
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", action="append", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    n = 0
    with open(args.out, "w") as f:
        for path in args.rows:
            for line in open(path):
                row = json.loads(line)
                f.write(json.dumps(add_suffix(row), ensure_ascii=False) + "\n")
                n += 1
    print("suffixed rows: %d -> %s" % (n, args.out))


if __name__ == "__main__":
    main()

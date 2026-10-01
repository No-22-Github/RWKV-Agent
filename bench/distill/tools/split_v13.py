#!/usr/bin/env python3
"""Hold out a validation split from suffixed v1.3 rows (v1.3 §M5).

  split_v13.py --rows <suffixed.jsonl> --train <train-rows.jsonl> --validation <val-rows.jsonl>

A row goes to validation when sha256(base case id) % 32 == 0, where the base id
is meta.case_id with any "--pN" path suffix removed. Splitting on the base id
keeps every path and every turn of one case on the same side, so the held-out
rows never share a workspace with training rows.
"""
import argparse
import hashlib
import json

SEPARATOR = "--p"


def base_id(case_id):
    cut = case_id.rfind(SEPARATOR)
    return case_id if cut < 0 else case_id[:cut]


def held_out(case_id):
    return int(hashlib.sha256(base_id(case_id).encode()).hexdigest(), 16) % 32 == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", required=True)
    ap.add_argument("--train", required=True)
    ap.add_argument("--validation", required=True)
    args = ap.parse_args()
    counts = {"train": 0, "validation": 0}
    with open(args.train, "w") as train, open(args.validation, "w") as val:
        for line in open(args.rows):
            row = json.loads(line)
            side = "validation" if held_out(row["meta"]["case_id"]) else "train"
            (val if side == "validation" else train).write(line)
            counts[side] += 1
    print("train %(train)d / validation %(validation)d" % counts)


if __name__ == "__main__":
    main()

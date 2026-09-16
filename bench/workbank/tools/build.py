#!/usr/bin/env python3
"""build.py — merge per-case case.json files into one canonical bank file.

Filters cases by tags.status, sorts by id, and writes
  {"schema_version": 5, "cases": [...]}
as compact sorted-key JSON. Prints the bank_version (sha256 over the exact
output file bytes) and the case count. Refuses to overwrite an existing --out
unless --force is given.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path


def find_case_files(root):
    root = Path(root)
    if (root / "case.json").is_file():
        return [root], [root / "case.json"]
    if not root.is_dir():
        raise NotADirectoryError(str(root))
    dirs = sorted({p.parent for p in root.rglob("case.json")}, key=lambda p: str(p))
    return dirs, [d / "case.json" for d in dirs]


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Merge case.json files into a canonical bank file with a bank_version hash.")
    ap.add_argument("--cases", required=True,
                    help="case root directory (searched recursively for case.json), or a single case dir")
    ap.add_argument("--status", choices=["draft", "reviewed", "frozen", "all"], default="all",
                    help="only include cases whose tags.status matches (default: all)")
    ap.add_argument("--out", required=True, help="output file path (refuses to overwrite without --force)")
    ap.add_argument("--force", action="store_true", help="overwrite an existing output file")
    args = ap.parse_args(argv)

    try:
        _, case_paths = find_case_files(args.cases)
    except NotADirectoryError:
        print("error: --cases %s is not a directory" % args.cases, file=sys.stderr)
        return 2

    cases, skipped, broken = [], 0, 0
    for path in case_paths:
        try:
            case = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print("warning: skipping unreadable %s: %s" % (path, exc), file=sys.stderr)
            broken += 1
            continue
        tags = case.get("tags") or {}
        status = tags.get("status")
        if args.status != "all" and status != args.status:
            skipped += 1
            continue
        cases.append(case)
    cases.sort(key=lambda c: str(c.get("id") or ""))

    payload = {"schema_version": 5, "cases": cases}
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")

    out = Path(args.out)
    if out.exists() and not args.force:
        print("error: %s already exists (use --force to overwrite)" % out, file=sys.stderr)
        return 2
    if out.parent and str(out.parent):
        out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)

    bank_version = "sha256:" + hashlib.sha256(data).hexdigest()
    print("cases: %d (skipped %d by status=%s, %d unreadable)"
          % (len(cases), skipped, args.status, broken))
    print("bank_version = %s" % bank_version)
    print("out: %s (%d bytes)" % (out, len(data)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

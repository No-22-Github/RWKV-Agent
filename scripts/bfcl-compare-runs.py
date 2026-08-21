#!/usr/bin/env python3
"""Compare deterministic fields from two RWKV-Agent BFCL runs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


COMPARE_FIELDS = (
    "prompt_sha256",
    "prefill_anchor",
    "assembly_mode",
    "generated_content",
    "content",
    "result",
    "model_calls",
    "parse_error",
    "error",
    "skipped",
)


def trace_path(value: str) -> Path:
    path = Path(value)
    if path.is_dir():
        path = path / "trace.jsonl"
    if not path.is_file():
        raise ValueError(f"BFCL trace does not exist: {path}")
    return path


def load_trace(path: Path) -> tuple[list[str], dict[str, dict[str, Any]]]:
    order: list[str] = []
    entries: dict[str, dict[str, Any]] = {}
    with path.open("r", encoding="utf-8") as source:
        for line_number, line in enumerate(source, 1):
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"decode {path}:{line_number}: {error}") from error
            case_id = entry.get("id")
            if not isinstance(case_id, str) or not case_id:
                raise ValueError(f"missing id in {path}:{line_number}")
            if case_id in entries:
                raise ValueError(f"duplicate id {case_id!r} in {path}")
            order.append(case_id)
            entries[case_id] = entry
    if not entries:
        raise ValueError(f"BFCL trace is empty: {path}")
    return order, entries


def compare(left_path: Path, right_path: Path) -> dict[str, Any]:
    left_order, left = load_trace(left_path)
    right_order, right = load_trace(right_path)
    missing_left = sorted(set(right) - set(left))
    missing_right = sorted(set(left) - set(right))
    order_equal = left_order == right_order
    mismatches: list[dict[str, Any]] = []
    for case_id in left_order:
        if case_id not in right:
            continue
        fields = [
            field
            for field in COMPARE_FIELDS
            if left[case_id].get(field) != right[case_id].get(field)
        ]
        if fields:
            mismatches.append({"id": case_id, "fields": fields})
    passed = not missing_left and not missing_right and order_equal and not mismatches
    return {
        "schema_version": 1,
        "left": str(left_path),
        "right": str(right_path),
        "total_left": len(left),
        "total_right": len(right),
        "order_equal": order_equal,
        "missing_left": missing_left,
        "missing_right": missing_right,
        "identical": len(left) - len(mismatches) - len(missing_right),
        "mismatches": mismatches,
        "passed": passed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare stable prompt/output/result fields in two BFCL trace files."
    )
    parser.add_argument("--left", required=True, help="left run directory or trace.jsonl")
    parser.add_argument("--right", required=True, help="right run directory or trace.jsonl")
    parser.add_argument("--output", help="optional JSON report path")
    args = parser.parse_args()
    try:
        report = compare(trace_path(args.left), trace_path(args.right))
    except ValueError as error:
        print(error, file=sys.stderr)
        return 2
    encoded = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output = Path(args.output)
        if output.exists():
            print(f"refusing to overwrite comparison report: {output}", file=sys.stderr)
            return 2
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8")
    else:
        sys.stdout.write(encoded)
    if report["passed"]:
        print(
            f"BFCL deterministic comparison passed: {report['identical']}/{report['total_left']}",
            file=sys.stderr,
        )
        return 0
    print(
        f"BFCL deterministic comparison failed: mismatches={len(report['mismatches'])} "
        f"missing_left={len(report['missing_left'])} missing_right={len(report['missing_right'])} "
        f"order_equal={report['order_equal']}",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

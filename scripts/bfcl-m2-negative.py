#!/usr/bin/env python3
import argparse
import json
import shutil
from pathlib import Path


MUTATIONS = {
    "unexpected-param": (
        "simple_python_0",
        "[calculate_triangle_area(base=10, height=5, bases=10)]",
    ),
    "missing-optional": (
        "simple_python_5",
        "[solve_quadratic(a=3, b=-11, c=-4)]",
    ),
    "lowercase-true": (
        "simple_python_55",
        '[biology.get_cell_info(cell_type="human", detailed=true)]',
    ),
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-result-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--mutation", required=True, choices=sorted(MUTATIONS))
    args = parser.parse_args()

    destination = args.output / "result"
    if args.output.exists():
        raise SystemExit(f"output already exists: {args.output}")
    shutil.copytree(args.source_result_dir, destination)

    result_path = (
        destination
        / "rwkv-agent-bfcl-ab-v1"
        / "non_live"
        / "BFCL_v4_simple_python_result.json"
    )
    entries = [json.loads(line) for line in result_path.read_text().splitlines() if line]
    target_id, replacement = MUTATIONS[args.mutation]
    matched = 0
    for entry in entries:
        if entry["id"] == target_id:
            entry["result"] = replacement
            matched += 1
    if len(entries) != 400 or matched != 1:
        raise SystemExit(f"expected 400 entries and one {target_id}, got {len(entries)} and {matched}")
    payload = "".join(json.dumps(entry, ensure_ascii=False) + "\n" for entry in entries)
    result_path.write_text(payload)


if __name__ == "__main__":
    main()

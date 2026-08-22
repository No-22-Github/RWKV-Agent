#!/usr/bin/env python3
"""Validate and merge per-case BFCL multi-turn artifacts for official scoring."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def load_single_jsonl(path: Path) -> tuple[dict[str, Any], bytes]:
    raw_lines = [line for line in path.read_bytes().splitlines() if line.strip()]
    if len(raw_lines) != 1:
        raise ValueError(f"{path}: expected exactly one non-empty JSONL record")
    value = json.loads(raw_lines[0])
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value, raw_lines[0]


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def natural_id_key(case_id: str) -> tuple[str, int, str]:
    match = re.fullmatch(r"(.*?)(\d+)", case_id)
    if match is None:
        return case_id, -1, case_id
    return match.group(1), int(match.group(2)), case_id


def write_new_or_identical(path: Path, data: bytes) -> None:
    if path.exists():
        if path.read_bytes() == data:
            return
        raise FileExistsError(f"refusing to replace non-identical archive artifact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(data)
    os.chmod(temporary, 0o600)
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--split", required=True)
    parser.add_argument("--expected-count", required=True, type=int)
    parser.add_argument(
        "--refresh-archive",
        action="store_true",
        help="atomically refresh archive.json after official scoring",
    )
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    case_dirs = sorted(
        (path.parent for path in run_dir.glob("case-*/run.json")),
        key=lambda path: natural_id_key(path.name),
    )
    if len(case_dirs) != args.expected_count:
        raise ValueError(
            f"{run_dir}: found {len(case_dirs)} cases, expected {args.expected_count}"
        )

    records: list[tuple[str, bytes]] = []
    ids: set[str] = set()
    config: dict[str, Any] | None = None
    summary_totals: Counter[str] = Counter()
    event_counts: Counter[str] = Counter()
    event_case_counts: Counter[str] = Counter()
    turn_exit_counts: Counter[str] = Counter()

    numeric_summary_fields = (
        "cases",
        "turns",
        "steps",
        "model_calls",
        "route_calls",
        "input_tokens",
        "output_tokens",
        "latency_seconds",
        "events",
    )

    for case_dir in case_dirs:
        manifest = load_json(case_dir / "run.json")
        summary = load_json(case_dir / "summary.json")
        trace, _ = load_single_jsonl(case_dir / "trace.jsonl")

        case_id = manifest.get("case_id")
        model_dir = manifest.get("model_dir_name")
        if not isinstance(case_id, str) or not isinstance(model_dir, str):
            raise ValueError(f"{case_dir}: run.json lacks case_id/model_dir_name")
        if manifest.get("split") != args.split:
            raise ValueError(f"{case_dir}: split differs from {args.split}")
        if case_id in ids:
            raise ValueError(f"duplicate case ID: {case_id}")
        ids.add(case_id)

        frozen = dict(manifest)
        frozen.pop("case_id", None)
        if config is None:
            config = frozen
        elif frozen != config:
            raise ValueError(f"{case_dir}: frozen run configuration differs")

        if summary.get("error"):
            raise ValueError(f"{case_dir}: summary records error {summary['error']!r}")
        if trace.get("id") != case_id or trace.get("category") != args.split:
            raise ValueError(f"{case_dir}: trace identity/category mismatch")

        result_path = (
            case_dir
            / "result"
            / model_dir
            / "multi_turn"
            / f"BFCL_v4_{args.split}_result.json"
        )
        result, result_raw = load_single_jsonl(result_path)
        if result.get("id") != case_id:
            raise ValueError(f"{result_path}: result ID differs from run.json")
        records.append((case_id, result_raw))

        for field in numeric_summary_fields:
            value = summary.get(field, 0)
            if not isinstance(value, (int, float)):
                raise ValueError(f"{case_dir}: summary field {field} is not numeric")
            summary_totals[field] += value
        case_event_kinds: set[str] = set()
        for event in trace.get("events", []):
            if isinstance(event, dict) and isinstance(event.get("kind"), str):
                event_counts[event["kind"]] += 1
                case_event_kinds.add(event["kind"])
        event_case_counts.update(case_event_kinds)
        for turn in trace.get("turns", []):
            if isinstance(turn, dict) and isinstance(turn.get("ended_by"), str):
                turn_exit_counts[turn["ended_by"]] += 1

    assert config is not None
    records.sort(key=lambda item: natural_id_key(item[0]))
    expected_ids = {f"{args.split}_{index}" for index in range(args.expected_count)}
    if ids != expected_ids:
        missing = sorted(expected_ids - ids, key=natural_id_key)
        extra = sorted(ids - expected_ids, key=natural_id_key)
        raise ValueError(f"non-contiguous IDs: missing={missing}, extra={extra}")

    merged = b"".join(raw + b"\n" for _, raw in records)
    model_dir = str(config["model_dir_name"])
    result_path = (
        run_dir
        / "result"
        / model_dir
        / "multi_turn"
        / f"BFCL_v4_{args.split}_result.json"
    )
    write_new_or_identical(result_path, merged)

    archive = {
        "schema_version": 1,
        "split": args.split,
        "case_count": len(records),
        "first_id": records[0][0],
        "last_id": records[-1][0],
        "result_path": str(result_path.relative_to(run_dir)),
        "result_sha256": sha256(merged),
        "run_config_sha256": sha256(canonical_bytes(config)),
        "run_config": config,
        "summary": dict(sorted(summary_totals.items())),
        "turn_exits": dict(sorted(turn_exit_counts.items())),
        "events": dict(sorted(event_counts.items())),
        "event_case_counts": dict(sorted(event_case_counts.items())),
    }
    score_path = (
        run_dir
        / "score"
        / model_dir
        / "multi_turn"
        / f"BFCL_v4_{args.split}_score.json"
    )
    if score_path.exists():
        score_lines = [line for line in score_path.read_bytes().splitlines() if line.strip()]
        score_records = [json.loads(line) for line in score_lines]
        if not score_records or not isinstance(score_records[0], dict):
            raise ValueError(f"{score_path}: missing official score summary")
        score_summary = score_records[0]
        correct = score_summary.get("correct_count")
        total = score_summary.get("total_count")
        accuracy = score_summary.get("accuracy")
        if total != args.expected_count or not isinstance(correct, int):
            raise ValueError(f"{score_path}: score summary does not match the archive")
        failures: Counter[str] = Counter()
        for record in score_records[1:]:
            if not isinstance(record, dict) or record.get("valid") is not False:
                raise ValueError(f"{score_path}: unexpected non-failure detail record")
            error = record.get("error", {})
            if not isinstance(error, dict) or not isinstance(error.get("error_type"), str):
                raise ValueError(f"{score_path}: failure detail lacks error_type")
            failures[error["error_type"]] += 1
        if correct + sum(failures.values()) != total:
            raise ValueError(f"{score_path}: score detail count does not match summary")
        score_artifacts = {
            str(path.relative_to(run_dir)): sha256(path.read_bytes())
            for path in sorted((run_dir / "score").rglob("*"))
            if path.is_file()
        }
        archive["official_score"] = {
            "accuracy": accuracy,
            "correct_count": correct,
            "total_count": total,
            "failure_types": dict(sorted(failures.items())),
            "artifacts_sha256": score_artifacts,
        }
    archive_bytes = json.dumps(archive, ensure_ascii=False, indent=2, sort_keys=True).encode(
        "utf-8"
    ) + b"\n"
    archive_path = run_dir / "archive.json"
    if args.refresh_archive and archive_path.exists():
        with tempfile.NamedTemporaryFile(dir=archive_path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(archive_bytes)
        os.chmod(temporary, 0o600)
        os.replace(temporary, archive_path)
    else:
        write_new_or_identical(archive_path, archive_bytes)
    print(json.dumps(archive, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

"""Case banks on disk, and normalized corpus records read as cases.

A bank is a directory tree of <id>/case.json files. Writing cases as a bank
(not a single cases.json) matters: agent-eval then takes the workbank suite
path and its defaults (rescue off, firstcall=auto), the same as a benchmark.
"""

from __future__ import annotations

import json
from pathlib import Path

from . import script, wire

REPO = Path(__file__).resolve().parents[2]
# Measured, never trained on.
TEST_BANK = REPO / "bench" / "workbank"


def load(root: Path) -> list[dict]:
    """Every case.json under root, in path order."""
    return [json.loads(path.read_text(encoding="utf-8")) for path in sorted(root.rglob("case.json"))]


def by_id(cases: list[dict]) -> dict[str, dict]:
    index = {}
    for case in cases:
        if case["id"] in index:
            raise ValueError(f"duplicate case id {case['id']}")
        index[case["id"]] = case
    return index


def write(root: Path, cases: list[dict]) -> None:
    for case in cases:
        case_dir = root / case["id"]
        case_dir.mkdir(parents=True)
        (case_dir / "case.json").write_text(json.dumps(case, ensure_ascii=False, indent=1))


def is_test_bank(path: Path) -> bool:
    return path.resolve().is_relative_to(TEST_BANK)


# Normalized records (datasets/workspace-agent-700-*/generated/normalized):
# one user turn, assistant messages of kind tool_call / no_tool / final.

def record_to_case(record: dict) -> dict:
    users = [m for m in record["messages"] if m["role"] == "user"]
    if len(users) != 1:
        raise ValueError(f"{record['id']}: expected one user turn, got {len(users)}")
    expected = record.get("expected") or {}
    case = {
        "id": record["id"],
        "description": f"{record.get('scenario', '')} corpus record {record['id']}",
        "category": record.get("scenario", ""),
        "files": record.get("initial_files") or {},
        "turns": [{"prompt": users[0]["text"], "expect": expected.get("turn_expectation") or {}}],
    }
    if record.get("web_fixture"):
        case["web_fixture"] = record["web_fixture"]
    if expected.get("case_expect"):
        case["expect"] = expected["case_expect"]
    return case


def record_to_script(record: dict) -> dict:
    texts, supervised = [], []
    for message in record["messages"]:
        if message["role"] != "assistant":
            continue
        if message["kind"] in ("tool_call", "no_tool"):
            texts.append(wire.tool_call(message["name"], message["arguments"]))
        elif message["kind"] == "final":
            texts.append(message["text"])
        else:
            raise ValueError(f"{record['id']}: unknown assistant kind {message['kind']!r}")
        supervised.append(bool(message.get("supervised")))
    return script.entry(record["id"], texts, supervised)

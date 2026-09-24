"""Reading agent-eval run directories (summary.json + trace.jsonl)."""

from __future__ import annotations

import collections
import json
from dataclasses import dataclass
from pathlib import Path

RETRY_EVENTS = {"protocol_retry"}


@dataclass
class CaseRun:
    case_id: str
    passed: bool
    turns: list[dict]  # agent.Result per turn, in turn order
    retries: int       # protocol retries across the case


def load(run_dir: Path) -> list[CaseRun]:
    passed = {case["id"]: case["passed"] for case in json.loads((run_dir / "summary.json").read_text())["cases"]}
    turns = collections.defaultdict(list)
    retries = collections.Counter()
    with (run_dir / "trace.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            if record["kind"] == "turn_result":
                turns[record["case_id"]].append((record["turn"], record["turn_result"]["result"]))
            elif record["kind"] == "runner_event" and record["runner_event"]["kind"] in RETRY_EVENTS:
                retries[record["case_id"]] += 1
    return [
        CaseRun(case_id, case_passed, [result for _, result in sorted(turns[case_id], key=lambda item: item[0])],
                retries[case_id])
        for case_id, case_passed in passed.items()
    ]

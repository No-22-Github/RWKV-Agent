#!/usr/bin/env python3
"""Run BFCL multi-turn base ground truth through the execution sidecar.

This validation-only script is the sole component here that reads
possible_answer. The runtime sidecar and Go agent loop do not.
"""

from __future__ import annotations

import argparse
import copy
import json
import subprocess
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


class Sidecar:
    def __init__(self, python: Path, script: Path, cwd: Path) -> None:
        self.process = subprocess.Popen(
            [str(python), "-u", str(script)],
            cwd=cwd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        self.request_id = 0

    def call(self, operation: str, **payload: Any) -> dict[str, Any]:
        self.request_id += 1
        request = {"request_id": self.request_id, "op": operation, **payload}
        assert self.process.stdin is not None
        assert self.process.stdout is not None
        self.process.stdin.write(json.dumps(request, ensure_ascii=False) + "\n")
        self.process.stdin.flush()
        line = self.process.stdout.readline()
        if not line:
            assert self.process.stderr is not None
            raise RuntimeError(f"sidecar exited: {self.process.stderr.read()}")
        response = json.loads(line)
        if response.get("request_id") != self.request_id or not response.get("ok"):
            raise RuntimeError(f"sidecar request failed: {response}")
        return response

    def close(self) -> None:
        if self.process.poll() is None:
            self.call("shutdown")
        self.process.wait(timeout=10)


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--python", type=Path, default=Path(".venv/bin/python"))
    parser.add_argument(
        "--sidecar", type=Path, default=Path("internal/bfcl/pysidecar/server.py")
    )
    parser.add_argument("--output", type=Path, default=Path("runs/bfcl-mt/e6-gt-selftest"))
    args = parser.parse_args()
    repo = args.repo.resolve()
    python = args.python if args.python.is_absolute() else repo / args.python
    sidecar_script = args.sidecar if args.sidecar.is_absolute() else repo / args.sidecar
    output = args.output if args.output.is_absolute() else repo / args.output
    data_dir = repo / "third_party/gorilla/berkeley-function-call-leaderboard/bfcl_eval/data"
    questions = load_jsonl(data_dir / "BFCL_v4_multi_turn_base.json")
    answers = load_jsonl(data_dir / "possible_answer/BFCL_v4_multi_turn_base.json")
    answer_by_id = {entry["id"]: entry["ground_truth"] for entry in answers}
    sidecar = Sidecar(python, sidecar_script, repo)
    positive: list[dict[str, Any]] = []
    try:
        for index, entry in enumerate(questions):
            ground_truth = answer_by_id[entry["id"]]
            sid = f"e6-{index}"
            sidecar.call(
                "new",
                sid=sid,
                initial_config=entry.get("initial_config", {}),
                involved_classes=entry["involved_classes"],
                long_context=False,
                test_entry_id=entry["id"],
            )
            for calls in ground_truth:
                response = sidecar.call("execute", sid=sid, calls=calls)
                errors = [value for value in response["results"] if value.startswith("Error during execution:")]
                if errors:
                    raise RuntimeError(f"{entry['id']} GT execution failed: {errors}")
            sidecar.call("close", sid=sid)
            positive.append(
                {
                    "id": entry["id"],
                    "result": [[list(calls)] for calls in ground_truth],
                }
            )
    finally:
        sidecar.close()

    positive_path = output / "positive/result/rwkv-agent-bfcl-ab-v1/multi_turn/BFCL_v4_multi_turn_base_result.json"
    write_jsonl(positive_path, positive)

    negative = copy.deepcopy(positive[0])
    negative["result"][0][0].append("mkdir(dir_name='unexpected_extra')")
    negative_path = output / "negative/result/rwkv-agent-bfcl-ab-v1/multi_turn/BFCL_v4_multi_turn_base_result.json"
    write_jsonl(negative_path, [negative])

    summary = {
        "schema_version": 1,
        "cases": len(positive),
        "sidecar_executed_ground_truth": len(positive),
        "execution_errors": 0,
        "positive_result": str(positive_path.relative_to(repo)),
        "negative_case": negative["id"],
        "negative_extra_call": "mkdir(dir_name='unexpected_extra')",
        "negative_result": str(negative_path.relative_to(repo)),
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

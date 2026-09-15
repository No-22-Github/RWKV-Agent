#!/usr/bin/env python3
"""Ablation-run analysis: per-category breakdown, run-to-run flips, prompt bytes.

Reads one or more agent-eval output directories (each containing run.json,
summary.json, trace.jsonl) and prints, per run:

- task_success split by case category (the bfcl-product three-way split:
  bfcl-irrelevance / bfcl-missing-required / bfcl-multiturn);
- headline metrics and the harness counters that explain them
  (forced answers, rejected/duplicate calls, repairs);
- prompt byte cost: the first decision prompt per case (the fixed harness
  prefix the ablations are trying to shrink) plus the per-case total.

With multiple runs it also prints the per-case flip matrix: which case ids
changed task_success between consecutive runs, so variance can be told apart
from signal.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_summary(run_dir: Path) -> dict:
    summary_path = run_dir / "summary.json"
    if not summary_path.is_file():
        raise SystemExit(f"missing {summary_path}")
    return json.loads(summary_path.read_text(encoding="utf-8"))


def case_success(case: dict) -> bool:
    return bool(case.get("passed"))


def irrelevance_gradient(case: dict, case_entries: list[dict]) -> dict:
    """Continuous movement metrics for one no-call-expected case.

    task_success is all-or-nothing and the category sits on the floor, so the
    ablation rounds are judged on these: average tool calls per case and how
    often the first decision step already opens a <tool_call>.
    """
    tool_call_steps = 0
    first_is_tool_call = False
    steps_seen = 0
    for entry in case_entries:
        if entry.get("kind") != "model_call":
            continue
        call = entry.get("model_call", {})
        stage = call.get("stage")
        text = call.get("response", {}).get("text", "") or ""
        if stage == "decision":
            steps_seen += 1
            if "<tool_call>" in text:
                tool_call_steps += 1
                if steps_seen == 1:
                    first_is_tool_call = True
    return {
        "tool_call_steps": tool_call_steps,
        "first_step_is_tool_call": first_is_tool_call,
    }


def irrelevance_gradient_from_trace(run_dir: Path, ids: list[str]) -> dict[str, dict]:
    """Read trace.jsonl once and collect per-case gradient metrics."""
    wanted = set(ids)
    by_case: dict[str, list[dict]] = {case_id: [] for case_id in ids}
    trace = run_dir / "trace.jsonl"
    if not trace.is_file():
        return {}
    with trace.open("r", encoding="utf-8") as source:
        for line in source:
            entry = json.loads(line)
            case_id = entry.get("case_id")
            if case_id in wanted:
                by_case[case_id].append(entry)
    return {case_id: irrelevance_gradient({"id": case_id}, entries) for case_id, entries in by_case.items()}


def prompt_bytes(case: dict) -> tuple[int, int]:
    """Return (first decision prompt bytes, total request bytes) for a case."""
    first = 0
    total = 0
    for turn in case.get("turns", []):
        steps = turn.get("result", {}).get("steps", [])
        for index, step in enumerate(steps):
            prompt = step.get("request", {}).get("prompt") or ""
            size = len(prompt.encode("utf-8"))
            if step.get("stage") == "decision" and index == 0 and first == 0:
                first = size
            total += size
    return first, total


def analyse_run(run_dir: Path) -> dict:
    summary = load_summary(run_dir)
    metrics = summary["metrics"]
    cases = summary["cases"]

    categories: dict[str, dict[str, int]] = {}
    first_bytes: dict[str, int] = {}
    total_bytes: dict[str, int] = {}
    for case in cases:
        category = case.get("category", "unknown")
        bucket = categories.setdefault(category, {"correct": 0, "total": 0})
        bucket["total"] += 1
        if case_success(case):
            bucket["correct"] += 1
        first_b, total_b = prompt_bytes(case)
        first_bytes[case["id"]] = first_b
        total_bytes[case["id"]] = total_b

    fixed_prefix = sorted(first_bytes.values())
    median_first = fixed_prefix[len(fixed_prefix) // 2] if fixed_prefix else 0

    irrelevance_ids = [case["id"] for case in cases if case.get("category") == "bfcl-irrelevance"]
    gradient = irrelevance_gradient_from_trace(run_dir, irrelevance_ids)

    return {
        "run_dir": str(run_dir),
        "task_success": metrics.get("task_success", {}),
        "answer_accuracy": metrics.get("answer_accuracy", {}),
        "protocol_validity": metrics.get("protocol_validity", {}),
        "forced_answers": metrics.get("forced_answers"),
        "rejected_tool_calls": metrics.get("rejected_tool_calls"),
        "duplicate_tool_calls": metrics.get("duplicate_tool_calls"),
        "tool_errors": metrics.get("tool_errors"),
        "model_calls": metrics.get("model_calls"),
        "tool_calls": metrics.get("tool_calls"),
        "repairs_by_id": metrics.get("repairs_by_id", {}),
        "categories": dict(sorted(categories.items())),
        "case_success": {case["id"]: case_success(case) for case in cases},
        "first_prompt_bytes": first_bytes,
        "total_prompt_bytes": total_bytes,
        "median_first_prompt_bytes": median_first,
        "sum_total_prompt_bytes": sum(total_bytes.values()),
        "irrelevance_gradient": gradient,
    }


def flip_matrix(runs: list[dict]) -> None:
    if len(runs) < 2:
        return
    print("\n## run-to-run flips (task_success)")
    base = runs[0]["case_success"]
    total_flips = 0
    for other in runs[1:]:
        flips = sorted(
            case_id
            for case_id, ok in base.items()
            if other["case_success"].get(case_id) != ok
        )
        total_flips += len(flips)
        print(f"- {Path(runs[0]['run_dir']).name} -> {Path(other['run_dir']).name}: {len(flips)} flips")
        for case_id in flips:
            print(f"    {case_id}: {base[case_id]} -> {other['case_success'][case_id]}")
    if len(runs) > 2:
        all_ids = sorted(base)
        unstable = [
            case_id
            for case_id in all_ids
            if len({run["case_success"].get(case_id) for run in runs}) > 1
        ]
        stable_true = [case_id for case_id in all_ids if all(run["case_success"].get(case_id) for run in runs)]
        stable_false = [
            case_id
            for case_id in all_ids
            if case_id not in stable_true and case_id not in unstable
        ]
        print(f"- cases unstable across {len(runs)} runs: {len(unstable)} -> {', '.join(unstable) if unstable else '-'}")
        print(f"- cases always pass: {len(stable_true)}, always fail: {len(stable_false)}")


def print_run(run: dict) -> None:
    print(f"\n# {run['run_dir']}")
    task = run["task_success"]
    print(
        f"task_success {task.get('correct', '?')}/{task.get('total', '?')} ({task.get('rate', 0):.1%})"
    )
    answer = run["answer_accuracy"]
    print(f"answer_accuracy {answer.get('correct', '?')}/{answer.get('total', '?')} ({answer.get('rate', 0):.1%})")
    print("category breakdown:")
    for category, bucket in run["categories"].items():
        print(f"  {category}: {bucket['correct']}/{bucket['total']}")
    print(
        "counters: model_calls={model_calls} tool_calls={tool_calls} "
        "forced_answers={forced_answers} rejected={rejected_tool_calls} "
        "duplicates={duplicate_tool_calls} tool_errors={tool_errors}".format(**run)
    )
    if run["repairs_by_id"]:
        print(f"repairs: {run['repairs_by_id']}")
    gradient = run.get("irrelevance_gradient") or {}
    if gradient:
        calls = [item["tool_call_steps"] for item in gradient.values()]
        first = sum(1 for item in gradient.values() if item["first_step_is_tool_call"])
        average = sum(calls) / len(calls) if calls else 0.0
        print(
            f"irrelevance gradient: {average:.2f} tool calls/case "
            f"(n={len(calls)}), first-step tool_call {first}/{len(calls)}"
        )
    print(
        f"prompt bytes: median first decision {run['median_first_prompt_bytes']}, "
        f"sum all requests {run['sum_total_prompt_bytes']}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs", nargs="+", type=Path, help="agent-eval output directories")
    args = parser.parse_args()
    runs = [analyse_run(run_dir) for run_dir in args.runs]
    for run in runs:
        print_run(run)
    flip_matrix(runs)


if __name__ == "__main__":
    main()

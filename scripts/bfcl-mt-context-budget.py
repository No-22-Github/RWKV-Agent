#!/usr/bin/env python3
"""Profile all BFCL v4 multi-turn prompts with ground-truth tool-result growth."""

from __future__ import annotations

import argparse
import copy
import json
import math
import re
import statistics
from collections import Counter
from pathlib import Path
from typing import Any

from bfcl_eval.constants.executable_backend_config import MULTI_TURN_FUNC_DOC_FILE_MAPPING
from bfcl_eval.eval_checker.multi_turn_eval import multi_turn_utils


SPLITS = ("base", "long_context", "miss_func", "miss_param")
CHARS_PER_TOKEN = 3.5
RWKV_USABLE_CONTEXT_TOKENS = 12_288
RWKV_CHAR_BUDGET = int(CHARS_PER_TOKEN * RWKV_USABLE_CONTEXT_TOKENS)
HOLDOUT_PROMPT = "I have updated some more functions you can choose from. What about now?"
SYSTEM_PREFIX = """System: You are a BFCL multi-turn tool agent. Use only the listed tools.
Return one JSON function-call object in exactly this shape: {"name":"TOOL_NAME","arguments":{"ARGUMENT":"VALUE"}}.
For parallel calls return a JSON array of those objects. The key is always "arguments", never "parameters" or "response". Do not predict tool results. Return [] when the current turn is complete. Output JSON only and no prose. Tool errors are evidence: correct the call instead of repeating it.
Tools:
["""


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def load_docs(data_dir: Path, entry: dict[str, Any]) -> list[dict[str, Any]]:
    excluded = set(entry.get("excluded_function", []))
    holdouts = {
        name: int(turn)
        for turn, names in entry.get("missed_function", {}).items()
        for name in names
    }
    docs: list[dict[str, Any]] = []
    for class_name in entry["involved_classes"]:
        path = data_dir / "multi_turn_func_doc" / MULTI_TURN_FUNC_DOC_FILE_MAPPING[class_name]
        for raw in load_jsonl(path):
            if raw["name"] not in excluded:
                raw.pop("response", None)
                docs.append({"class": class_name, "name": raw["name"], "raw": raw, "holdout": holdouts.get(raw["name"])})
    return docs


def call_classes(calls: list[str], docs: list[dict[str, Any]]) -> list[str]:
    mapping = {doc["name"]: doc["class"] for doc in docs}
    result: list[str] = []
    for call in calls:
        match = re.match(r"\s*([A-Za-z_]\w*)\s*\(", call)
        if match and mapping.get(match.group(1)) not in result:
            result.append(mapping[match.group(1)])
    return result


def render_prefix(entry: dict[str, Any], docs: list[dict[str, Any]], turn: int, narrowed: list[str] | None) -> str:
    available = [
        doc["raw"]
        for doc in docs
        if (doc["holdout"] is None or turn >= doc["holdout"])
        and (narrowed is None or doc["class"] in narrowed)
    ]
    encoded_tools = ",\n".join(
        json.dumps(item, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        for item in available
    )
    return (
        SYSTEM_PREFIX
        + encoded_tools
        + "\n]\nInitial state:\n"
        + json.dumps(entry.get("initial_config", {}), ensure_ascii=False, separators=(",", ":"))
        + "\n"
    )


def transcript_message(role: str, content: Any) -> str:
    if not isinstance(content, str):
        content = json.dumps(content, ensure_ascii=False, separators=(",", ":"))
    return f"{role}: {content}\n"


def execute(entry: dict[str, Any], calls: list[str], split: str, suffix: str) -> list[str]:
    results, _ = multi_turn_utils.execute_multi_turn_func_call(
        calls,
        entry.get("initial_config", {}),
        entry["involved_classes"],
        f"rwkv_agent_context_{suffix}",
        entry["id"],
        long_context=split == "long_context",
        is_evaL_run=False,
    )
    return results


def cleanup(entry: dict[str, Any], suffix: str) -> None:
    prefix = re.sub(r"[-./:]", "_", f"rwkv_agent_context_{suffix}_{entry['id']}_")
    for name in list(vars(multi_turn_utils)):
        if name.startswith(prefix) and name.endswith("_instance"):
            delattr(multi_turn_utils, name)


def profile_case(entry: dict[str, Any], ground_truth: list[list[str]], docs: list[dict[str, Any]], split: str, index: int) -> dict[str, Any]:
    history = ""
    full_max = 0
    narrow_max = 0
    result_bytes = 0
    suffix = f"{split}_{index}"
    try:
        for turn, original_messages in enumerate(entry["question"]):
            messages = original_messages or [{"role": "user", "content": HOLDOUT_PROMPT}]
            for message in messages:
                history += transcript_message(message["role"].title(), message["content"])
            calls = ground_truth[turn]
            narrowed = call_classes(calls, docs)
            full_max = max(full_max, len(render_prefix(entry, docs, turn, None) + history + "Assistant: "))
            narrow_max = max(narrow_max, len(render_prefix(entry, docs, turn, narrowed) + history + "Assistant: "))
            if calls:
                results = execute(entry, calls, split, suffix)
                result_bytes += len(json.dumps(results, ensure_ascii=False))
                history += transcript_message("Assistant", calls)
                history += transcript_message("Tool", results)
                full_max = max(full_max, len(render_prefix(entry, docs, turn, None) + history + "Assistant: "))
                narrow_max = max(narrow_max, len(render_prefix(entry, docs, turn, narrowed) + history + "Assistant: "))
    finally:
        cleanup(entry, suffix)
    return {
        "id": entry["id"],
        "split": split,
        "turns": len(entry["question"]),
        "classes": sorted(entry["involved_classes"]),
        "initial_config_chars": len(json.dumps(entry.get("initial_config", {}), ensure_ascii=False)),
        "gt_result_chars": result_bytes,
        "full_max_chars": full_max,
        "narrow_max_chars": narrow_max,
        "full_est_tokens": math.ceil(full_max / CHARS_PER_TOKEN),
        "narrow_est_tokens": math.ceil(narrow_max / CHARS_PER_TOKEN),
        "full_feasible": full_max <= RWKV_CHAR_BUDGET,
        "narrow_feasible": narrow_max <= RWKV_CHAR_BUDGET,
    }


def percentile(values: list[int], fraction: float) -> int:
    values = sorted(values)
    return values[max(0, math.ceil(fraction * len(values)) - 1)]


def aggregate(rows: list[dict[str, Any]], field: str) -> dict[str, Any]:
    values = [row[field] for row in rows]
    return {
        "p50": int(statistics.median(values)),
        "p90": percentile(values, 0.90),
        "p95": percentile(values, 0.95),
        "max": max(values),
    }


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# BFCL v4 multi-turn E5 context budget",
        "",
        f"- Cases: {report['cases']} (200 per split).",
        f"- Conservative estimate: {CHARS_PER_TOKEN:.1f} characters/token; RWKV usable budget {RWKV_USABLE_CONTEXT_TOKENS} tokens = {RWKV_CHAR_BUDGET} characters.",
        "- `full`: all involved-class tool docs available at that turn. `narrow`: ideal GT-class catalog for that turn; this is a feasibility bound, not a model-routing score.",
        "- Prompt growth includes initial_config, all user turns, GT calls, and actual official-backend GT execution results. `path` is not rendered.",
        "",
        "| Split | Turns distribution | Full chars p50/p90/p95/max | Full feasible | Narrow chars p50/p90/p95/max | Narrow feasible |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for split in SPLITS:
        item = report["splits"][split]
        full = item["full_chars"]
        narrow = item["narrow_chars"]
        turns = ", ".join(f"{key}:{value}" for key, value in item["turns"].items())
        lines.append(
            f"| `{split}` | {turns} | {full['p50']}/{full['p90']}/{full['p95']}/{full['max']} | {item['full_feasible']}/200 | {narrow['p50']}/{narrow['p90']}/{narrow['p95']}/{narrow['max']} | {item['narrow_feasible']}/200 |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- Full-catalog feasible set: {report['full_feasible_ids_count']}/800.",
            f"- Ideal class-narrowed feasible set: {report['narrow_feasible_ids_count']}/800.",
            f"- Common feasible set for baseline/enhanced RWKV comparison: {report['common_feasible_ids_count']}/800 (the full-catalog set).",
            "- E7 `multi_turn_base_0` is inside both feasible sets. E8 should freeze a manifest from the common feasible IDs; Qwen comparisons should use that same common subset even though its server context can be larger.",
            "",
            "Machine-readable details: `context-budget.json`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, default=Path("runs/bfcl-mt/context-budget.md"))
    args = parser.parse_args()
    repo = args.repo.resolve()
    output = args.output if args.output.is_absolute() else repo / args.output
    data_dir = repo / "third_party/gorilla/berkeley-function-call-leaderboard/bfcl_eval/data"
    all_rows: list[dict[str, Any]] = []
    for split in SPLITS:
        questions = load_jsonl(data_dir / f"BFCL_v4_multi_turn_{split}.json")
        answers = {row["id"]: row["ground_truth"] for row in load_jsonl(data_dir / f"possible_answer/BFCL_v4_multi_turn_{split}.json")}
        for index, entry in enumerate(questions):
            all_rows.append(profile_case(entry, answers[entry["id"]], load_docs(data_dir, entry), split, index))
    report: dict[str, Any] = {"schema_version": 1, "cases": len(all_rows), "rows": all_rows, "splits": {}}
    for split in SPLITS:
        rows = [row for row in all_rows if row["split"] == split]
        report["splits"][split] = {
            "turns": dict(sorted(Counter(row["turns"] for row in rows).items())),
            "full_chars": aggregate(rows, "full_max_chars"),
            "narrow_chars": aggregate(rows, "narrow_max_chars"),
            "full_feasible": sum(row["full_feasible"] for row in rows),
            "narrow_feasible": sum(row["narrow_feasible"] for row in rows),
        }
    full_ids = {row["id"] for row in all_rows if row["full_feasible"]}
    narrow_ids = {row["id"] for row in all_rows if row["narrow_feasible"]}
    report["full_feasible_ids_count"] = len(full_ids)
    report["narrow_feasible_ids_count"] = len(narrow_ids)
    report["common_feasible_ids_count"] = len(full_ids & narrow_ids)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(markdown(report))
    output.with_suffix(".json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(output.read_text())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

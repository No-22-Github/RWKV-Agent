#!/usr/bin/env python3
"""Turn teacher agent-eval runs into a replay script for harness_corpus.py.

A teacher model (for example DeepSeek over chat-completions, native tool
calling) runs a bank of distillation cases k times; this script keeps the
passing, clean trajectories, normalizes their arguments to the corpus style,
de-duplicates them, and writes one script entry per kept path:

    python3 scripts/trace2script.py --run runs/distill/k0 --run runs/distill/k1 \
        --out runs/distill/script.jsonl --report runs/distill/paths.jsonl

Only actions cross over (tool name, arguments, final text). The teacher's
own wire, reasoning and receipts stay behind: harness_corpus.py replays the
actions through the student's wire and re-executes every tool.

Path selection per case: drop failing or unclean paths, drop exact action
duplicates, then keep the shortest path first and further paths only when
their tool sequence differs, up to --max-per-case. Script case IDs are
"<case id>--p<n>".
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

PATH_SEPARATOR = "--p"

# Arguments equal to the work-v1 implementation defaults carry no
# information; teachers that fill every schema field would otherwise teach
# the student to spell them out. Values from internal/agent/tools.go and
# internal/agent/tools/{web,assistant}.go.
DEFAULTS = {
    "list_files": {"path": "", "max_depth": 3, "max_results": 200},
    "search_text": {"path": "", "case_sensitive": False, "max_results": 50},
    "web_search": {"max_results": 5},
}
# Optional arguments whose empty value means "not given".
EMPTY_MEANS_ABSENT = {
    "read_lines": {"start_line", "end_line"},
    "calculator": {"precision"},
    "data_query": {"filter", "select", "group_by", "operation", "field", "expression"},
}


def normalize_arguments(name: str, arguments: dict) -> dict:
    defaults = DEFAULTS.get(name, {})
    optional = EMPTY_MEANS_ABSENT.get(name, set())
    kept = {}
    for key, value in arguments.items():
        if value is None:
            continue
        if key in defaults and value == defaults[key] and type(value) is type(defaults[key]):
            continue
        if key in optional and value in ("", {}, []):
            continue
        kept[key] = value
    return kept


def compact_call(name: str, arguments: dict) -> str:
    """Same bytes as scripts/harness_corpus.compact_call."""
    payload = json.dumps({"name": name, "arguments": arguments}, ensure_ascii=False, separators=(",", ":"))
    return f"<tool_call>{payload}</tool_call>"


def load_run(run_dir: Path):
    """Yield (case_id, passed, turns) with each turn's result and outcome."""
    passed = {case["id"]: case["passed"] for case in json.loads((run_dir / "summary.json").read_text())["cases"]}
    turns = collections.defaultdict(list)
    retries = collections.Counter()
    with (run_dir / "trace.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            if record["kind"] == "turn_result":
                turns[record["case_id"]].append((record["turn"], record["turn_result"]))
            elif record["kind"] == "runner_event" and record["runner_event"]["kind"] in ("protocol_retry", "route_retry"):
                retries[record["case_id"]] += 1
    for case_id, case_passed in passed.items():
        ordered = [result for _, result in sorted(turns.get(case_id, []), key=lambda item: item[0])]
        yield case_id, case_passed, ordered, retries[case_id]


def extract_path(turns: list, retries: int) -> tuple[list[str] | None, str]:
    """The script outputs of one run of one case, or None and the reason."""
    if retries:
        return None, "protocol retry"
    outputs = []
    for turn in turns:
        result = turn["result"]
        steps = result.get("steps") or []
        if not steps:
            return None, "turn without steps"
        for index, step in enumerate(steps):
            if step.get("stage") != "decision":
                return None, f"{step.get('stage')} stage (forced closeout)"
            action = step.get("action_type")
            if action == "tool":
                if step.get("tool_error") or step.get("tool_rejected_reason") or not step.get("tool_executed"):
                    return None, "tool error or rejection"
                arguments = step.get("tool_arguments") or {}
                if not isinstance(arguments, dict):
                    return None, "non-object tool arguments"
                outputs.append(compact_call(step["tool"], normalize_arguments(step["tool"], arguments)))
            elif action == "final":
                if index != len(steps) - 1:
                    return None, "final before the last step"
                text = (step.get("model_output") or "").strip()
                if text != (result.get("output") or "").strip():
                    return None, "answer repaired by the harness"
                if not text:
                    return None, "empty final answer"
                outputs.append(text)
            else:
                return None, f"action {action!r}"
    return outputs, ""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", type=Path, action="append", required=True, help="teacher agent-eval run (repeatable)")
    parser.add_argument("--out", type=Path, required=True, help="new script JSONL")
    parser.add_argument("--report", type=Path, help="optional per-case JSONL: pass@k, kept paths, drop reasons")
    parser.add_argument("--max-per-case", type=int, default=2)
    args = parser.parse_args()

    candidates = collections.defaultdict(list)  # case -> [(outputs, run index)]
    stats = collections.defaultdict(lambda: {"runs": 0, "passed": 0, "drops": collections.Counter()})
    for run_index, run_dir in enumerate(args.run):
        for case_id, passed, turns, retries in load_run(run_dir):
            if PATH_SEPARATOR in case_id:
                raise SystemExit(f"case id {case_id!r} contains the reserved separator {PATH_SEPARATOR!r}")
            stat = stats[case_id]
            stat["runs"] += 1
            if not passed:
                stat["drops"]["failed"] += 1
                continue
            stat["passed"] += 1
            outputs, reason = extract_path(turns, retries)
            if outputs is None:
                stat["drops"][reason] += 1
                continue
            candidates[case_id].append((outputs, run_index))

    entries, report = [], []
    for case_id in sorted(stats):
        stat = stats[case_id]
        seen_actions, seen_shapes, kept = set(), set(), []
        # Shortest first; ties keep run order so the result is deterministic.
        for outputs, _ in sorted(candidates[case_id], key=lambda item: (len(item[0]), item[1])):
            actions = tuple(outputs)
            if actions in seen_actions:
                stat["drops"]["duplicate path"] += 1
                continue
            seen_actions.add(actions)
            shape = tuple(json.loads(o[len("<tool_call>"):-len("</tool_call>")])["name"]
                          if o.startswith("<tool_call>") else "final" for o in outputs)
            if kept and shape in seen_shapes:
                stat["drops"]["same tool sequence"] += 1
                continue
            if len(kept) >= args.max_per_case:
                stat["drops"]["over per-case cap"] += 1
                continue
            seen_shapes.add(shape)
            kept.append(outputs)
        for number, outputs in enumerate(kept, 1):
            entries.append({
                "case_id": f"{case_id}{PATH_SEPARATOR}{number}",
                "outputs": [{"text": text, "supervised": True} for text in outputs],
            })
        report.append({"case_id": case_id, "runs": stat["runs"], "passed": stat["passed"],
                       "kept": len(kept), "steps": [len(o) for o in kept], "drops": dict(stat["drops"])})

    with args.out.open("x", encoding="utf-8") as handle:
        for entry in entries:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    if args.report:
        with args.report.open("x", encoding="utf-8") as handle:
            for row in report:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    drops = collections.Counter()
    for stat in stats.values():
        drops.update(stat["drops"])
    pass_at = collections.Counter((row["passed"], row["runs"]) for row in report)
    print(f"trace2script: {len(stats)} cases, {len(entries)} paths kept "
          f"({sum(1 for row in report if row['kept'])} cases with at least one)")
    print("  pass@k: " + ", ".join(f"{p}/{k}: {n}" for (p, k), n in sorted(pass_at.items())))
    for reason, count in drops.most_common():
        print(f"  {count:5d}  dropped: {reason}")
    never = [row["case_id"] for row in report if row["passed"] == 0]
    if never:
        print(f"  {len(never)} cases never passed (check the case before distilling): {' '.join(never[:20])}"
              + (" …" if len(never) > 20 else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Pick teacher paths out of agent-eval runs and write them as a replay script.

A teacher (for example DeepSeek over chat-completions, native tool calling)
runs a bank of distillation cases k times; each passing, clean run of a case
is a candidate path:

    python3 -m scripts.corpus paths --run runs/distill/k0 --run runs/distill/k1 \\
        --out runs/distill/script.jsonl --report runs/distill/paths.jsonl

Only actions cross over (tool name, arguments, final text). The teacher's
own wire, reasoning and receipts stay behind: render replays the actions
through the student's wire and re-executes every tool.

Per case: drop failing or unclean runs and exact duplicates, then keep the
shortest path first and further paths only when their tool sequence differs,
up to --max-per-case. Script case IDs are "<case id>--p<n>".
"""

from __future__ import annotations

import collections
from dataclasses import dataclass, field
from pathlib import Path

from . import jsonl, runs, script, wire

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


@dataclass(frozen=True)
class Action:
    text: str               # the generation's raw output
    tool: str | None = None  # None for a final answer


Trajectory = tuple[Action, ...]


class Unclean(Exception):
    """A passing run whose path cannot be replayed as-is; the message is the drop reason."""


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


def extract(run: runs.CaseRun) -> Trajectory:
    """The actions of one passing run, or Unclean."""
    if run.retries:
        raise Unclean("protocol retry")
    actions = []
    for result in run.turns:
        steps = result.get("steps") or []
        if not steps:
            raise Unclean("turn without steps")
        for index, step in enumerate(steps):
            if step.get("stage") != "decision":
                raise Unclean(f"{step.get('stage')} stage (forced closeout)")
            kind = step.get("action_type")
            if kind == "tool":
                if step.get("tool_error") or step.get("tool_rejected_reason") or not step.get("tool_executed"):
                    raise Unclean("tool error or rejection")
                arguments = step.get("tool_arguments") or {}
                if not isinstance(arguments, dict):
                    raise Unclean("non-object tool arguments")
                name = step["tool"]
                actions.append(Action(wire.tool_call(name, normalize_arguments(name, arguments)), name))
            elif kind == "final":
                if index != len(steps) - 1:
                    raise Unclean("final before the last step")
                text = (step.get("model_output") or "").strip()
                if text != (result.get("output") or "").strip():
                    raise Unclean("answer repaired by the harness")
                if not text:
                    raise Unclean("empty final answer")
                actions.append(Action(text))
            else:
                raise Unclean(f"action {kind!r}")
    return tuple(actions)


@dataclass
class CaseStats:
    runs: int = 0
    passed: int = 0
    drops: collections.Counter = field(default_factory=collections.Counter)
    candidates: list[tuple[Trajectory, int]] = field(default_factory=list)  # (path, run index)


def collect(run_dirs: list[Path]) -> dict[str, CaseStats]:
    stats = collections.defaultdict(CaseStats)
    for run_index, run_dir in enumerate(run_dirs):
        for run in runs.load(run_dir):
            if script.PATH_SEPARATOR in run.case_id:
                raise SystemExit(f"case id {run.case_id!r} contains the reserved separator {script.PATH_SEPARATOR!r}")
            stat = stats[run.case_id]
            stat.runs += 1
            if not run.passed:
                stat.drops["failed"] += 1
                continue
            stat.passed += 1
            try:
                stat.candidates.append((extract(run), run_index))
            except Unclean as reason:
                stat.drops[str(reason)] += 1
    return stats


def select(stat: CaseStats, max_per_case: int) -> list[Trajectory]:
    """Shortest first (ties in run order), then only new tool sequences, up to the cap."""
    seen, shapes, kept = set(), set(), []
    for path, _ in sorted(stat.candidates, key=lambda item: (len(item[0]), item[1])):
        if path in seen:
            stat.drops["duplicate path"] += 1
            continue
        seen.add(path)
        shape = tuple(action.tool or "final" for action in path)
        if kept and shape in shapes:
            stat.drops["same tool sequence"] += 1
            continue
        if len(kept) >= max_per_case:
            stat.drops["over per-case cap"] += 1
            continue
        shapes.add(shape)
        kept.append(path)
    return kept


def add_arguments(parser) -> None:
    parser.add_argument("--run", type=Path, action="append", required=True, help="teacher agent-eval run (repeatable)")
    parser.add_argument("--out", type=Path, required=True, help="new script JSONL")
    parser.add_argument("--report", type=Path, help="optional per-case JSONL: pass@k, kept paths, drop reasons")
    parser.add_argument("--max-per-case", type=int, default=2)


def run(args) -> int:
    stats = collect(args.run)
    entries, report = [], []
    for case_id in sorted(stats):
        stat = stats[case_id]
        kept = select(stat, args.max_per_case)
        entries += [script.entry(script.path_id(case_id, number), [action.text for action in path])
                    for number, path in enumerate(kept, 1)]
        report.append({"case_id": case_id, "runs": stat.runs, "passed": stat.passed,
                       "kept": len(kept), "steps": [len(path) for path in kept], "drops": dict(stat.drops)})

    jsonl.write(args.out, entries)
    if args.report:
        jsonl.write(args.report, report)
    print_summary(stats, entries, report)
    return 0


def print_summary(stats: dict[str, CaseStats], entries: list[dict], report: list[dict]) -> None:
    drops = collections.Counter()
    for stat in stats.values():
        drops.update(stat.drops)
    pass_at = collections.Counter((row["passed"], row["runs"]) for row in report)
    print(f"paths: {len(stats)} cases, {len(entries)} paths kept "
          f"({sum(1 for row in report if row['kept'])} cases with at least one)")
    print("  pass@k: " + ", ".join(f"{p}/{k}: {n}" for (p, k), n in sorted(pass_at.items())))
    for reason, count in drops.most_common():
        print(f"  {count:5d}  dropped: {reason}")
    never = [row["case_id"] for row in report if row["passed"] == 0]
    if never:
        print(f"  {len(never)} cases never passed (check the case before distilling): {' '.join(never[:20])}"
              + (" …" if len(never) > 20 else ""))

#!/usr/bin/env python3
"""Render normalized corpus records through the real eval harness.

Instead of re-implementing the wire in Python (tooling/workv1_wire.py), this
replays each record's teacher actions through `rwkv-cli agent-eval --script`
under the same flags a workbank benchmark uses, then lets `tracecorpus` cut
training rows out of the resulting trace. Every byte between teacher actions
(tool receipts, post-tool reminders, RECOVERY notes, duplicate rejections,
forced-answer blocks) is therefore exactly what the model sees at eval time.

    python3 scripts/harness_corpus.py \
        --records datasets/workspace-agent-700-20260920/generated/normalized/train.jsonl \
        --out runs/harness-corpus-train

or, for teacher-distilled paths (scripts/trace2script.py output, case IDs
"<case id>--p<n>" resolved against a bank directory of distillation cases):

    python3 scripts/harness_corpus.py --cases bench/distill/cases \
        --script runs/distill/script.jsonl --out runs/distill/corpus

Writes into --out (must not exist): cases/<id>/case.json (a bank directory,
so agent-eval takes the same workbank suite path and defaults as a benchmark),
script.jsonl, run/ (the agent-eval artifacts), rows.jsonl and rejects.jsonl.
Extra agent-eval flags (for example a different --profile or --wire) go
after `--`.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
# The test bank is measured, never trained on; rendering it needs an explicit
# flag (pipeline smoke tests only).
TEST_BANK = REPO / "bench" / "workbank"

# The workbank arm of .claude/skills/rwkv-bench/sweep.py: catalog, file tools,
# budgets and wire. Sampling flags are omitted because a script ignores them.
BENCH_FLAGS = [
    "--tool-catalog", "work-v1", "--file-tools", "lines",
    "--max-steps", "16", "--max-tokens", "4096", "--decision-max-tokens", "2048",
    "--profile", "g1k", "--strict-spec",
    "--trace-prompt-bytes", "-1",
]


def compact_call(name: str, arguments: dict) -> str:
    """Same bytes as tooling/workv1_wire.compact_call: name first, compact JSON."""
    payload = json.dumps({"name": name, "arguments": arguments}, ensure_ascii=False, separators=(",", ":"))
    return f"<tool_call>{payload}</tool_call>"


def to_case_and_script(record: dict) -> tuple[dict, dict]:
    messages = record["messages"]
    users = [m for m in messages if m["role"] == "user"]
    if len(users) != 1:
        raise ValueError(f"{record['id']}: expected one user turn, got {len(users)}")
    outputs = []
    for message in messages:
        if message["role"] != "assistant":
            continue
        if message["kind"] in ("tool_call", "no_tool"):
            text = compact_call(message["name"], message["arguments"])
        elif message["kind"] == "final":
            text = message["text"]
        else:
            raise ValueError(f"{record['id']}: unknown assistant kind {message['kind']!r}")
        outputs.append({"text": text, "supervised": bool(message.get("supervised"))})
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
    return case, {"case_id": record["id"], "outputs": outputs}


def cases_for_script(cases_dir: Path, script_path: Path) -> tuple[list[dict], list[dict]]:
    """One case copy per script entry; "<id>--p<n>" resolves to case <id>."""
    bank = {}
    for path in cases_dir.rglob("case.json"):
        case = json.loads(path.read_text(encoding="utf-8"))
        if case["id"] in bank:
            raise ValueError(f"duplicate case id {case['id']} in {cases_dir}")
        bank[case["id"]] = case
    cases, script = [], []
    for line in script_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        entry = json.loads(line)
        base = entry["case_id"].rsplit("--p", 1)[0] if "--p" in entry["case_id"] else entry["case_id"]
        if base not in bank:
            raise ValueError(f"script entry {entry['case_id']} has no case {base} in {cases_dir}")
        cases.append({**bank[base], "id": entry["case_id"]})
        script.append(entry)
    return cases, script


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--records", type=Path, help="normalized records JSONL")
    parser.add_argument("--cases", type=Path, help="bank directory the --script case IDs resolve against")
    parser.add_argument("--script", type=Path, help="replay script (trace2script.py output)")
    parser.add_argument("--out", type=Path, required=True, help="new output directory")
    parser.add_argument("--cli", type=Path, default=REPO / "bin" / "rwkv-cli")
    parser.add_argument("--tracecorpus", type=Path, default=REPO / "bin" / "tracecorpus")
    parser.add_argument("--parallelism", type=int, default=32)
    parser.add_argument("--allow-test-bank", action="store_true",
                        help="permit --cases inside bench/workbank (pipeline smoke tests; never train on the output)")
    parser.add_argument("--keep-failing", action="store_true",
                        help="also emit rows whose teacher trajectory fails the case expectations")
    parser.add_argument("extra", nargs="*", help="extra agent-eval flags after --")
    args = parser.parse_args()

    if bool(args.records) == bool(args.cases or args.script) or bool(args.cases) != bool(args.script):
        parser.error("give either --records, or both --cases and --script")
    if args.cases and args.cases.resolve().is_relative_to(TEST_BANK) and not args.allow_test_bank:
        parser.error(f"--cases {args.cases} is the test bank; distill from a separate bank "
                     "(pass --allow-test-bank only for a smoke test)")
    args.out.mkdir(parents=True, exist_ok=False)
    cases, script = [], []
    if args.records:
        for line in args.records.read_text(encoding="utf-8").splitlines():
            if line.strip():
                case, entry = to_case_and_script(json.loads(line))
                cases.append(case)
                script.append(entry)
    else:
        cases, script = cases_for_script(args.cases, args.script)
    cases_path = args.out / "cases"
    for case in cases:
        case_dir = cases_path / case["id"]
        case_dir.mkdir(parents=True)
        (case_dir / "case.json").write_text(
            json.dumps(case, ensure_ascii=False, indent=1))
    script_path = args.out / "script.jsonl"
    script_path.write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in script))

    # The bank loader enforces authoring rules (for example an expect.run
    # script must ship in files) that some corpus trajectories cannot meet
    # without changing the workspace the teacher saw. Let the real validator
    # decide: set aside each case it rejects, with its reason, and retry.
    load_rejects = set_aside_unloadable(args.cli, cases_path, args.out / "unloadable")
    for case_id, reason in load_rejects:
        print(f"unloadable {case_id}: {reason}", file=sys.stderr)

    run_dir = args.out / "run"
    eval_cmd = [str(args.cli), "agent-eval", "--script", str(script_path), "--cases", str(cases_path),
                "--include-draft", "--case-parallelism", str(args.parallelism), "--output", str(run_dir),
                *BENCH_FLAGS, *args.extra]
    print("+", " ".join(eval_cmd), file=sys.stderr)
    # agent-eval exits nonzero when cases fail; the teacher's failures are
    # reported by tracecorpus, so only a missing run directory is fatal.
    subprocess.run(eval_cmd, cwd=REPO)
    if not (run_dir / "trace.jsonl").is_file():
        print("agent-eval produced no trace", file=sys.stderr)
        return 1
    corpus_cmd = [str(args.tracecorpus), "--run", str(run_dir), "--script", str(script_path),
                  "--out", str(args.out / "rows.jsonl"), "--rejects", str(args.out / "rejects.jsonl")]
    if args.keep_failing:
        corpus_cmd.append("--require-pass=false")
    code = subprocess.run(corpus_cmd, cwd=REPO).returncode
    if load_rejects:
        with (args.out / "rejects.jsonl").open("a", encoding="utf-8") as handle:
            for case_id, reason in load_rejects:
                handle.write(json.dumps({"case_id": case_id, "reason": "unloadable: " + reason},
                                        ensure_ascii=False) + "\n")
        print(f"  {len(load_rejects):4d}  unloadable by the bank loader (see rejects.jsonl)")
    return code


_LOAD_ERROR = re.compile(r"cases/([^/]+)/case\.json: (.*)")


def set_aside_unloadable(cli: Path, cases_path: Path, parking: Path) -> list[tuple[str, str]]:
    """Move cases the bank loader rejects out of cases_path until it loads."""
    rejected = []
    while True:
        probe = subprocess.run(
            [str(cli), "agent-eval", "--script", "/dev/null", "--cases", str(cases_path), "--include-draft",
             "--output", str(parking.parent / ".load-probe"), *BENCH_FLAGS],
            cwd=REPO, capture_output=True, text=True)
        match = _LOAD_ERROR.search(probe.stderr + probe.stdout)
        if not match or "load Agent eval cases" not in probe.stderr + probe.stdout:
            return rejected
        case_id, reason = match.group(1), match.group(2).strip()
        parking.mkdir(exist_ok=True)
        shutil.move(str(cases_path / case_id), str(parking / case_id))
        rejected.append((case_id, reason))


if __name__ == "__main__":
    sys.exit(main())

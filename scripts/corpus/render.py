"""Render corpus rows by replaying teacher actions through the real eval harness.

Instead of re-implementing the wire in Python, this replays each script
entry through `rwkv-cli agent-eval --script` under the flags a workbank
benchmark uses, then lets `tracecorpus` cut training rows out of the trace.
Every byte between teacher actions (tool receipts, post-tool reminders,
RECOVERY notes, duplicate rejections, forced-answer blocks) is therefore
exactly what the model sees at eval time.

    python3 -m scripts.corpus render --cases bench/distill/cases \\
        --script runs/distill/script.jsonl --out runs/distill/corpus
    python3 -m scripts.corpus render \\
        --records datasets/workspace-agent-700-20260920/generated/normalized/train.jsonl \\
        --out runs/harness-corpus-train

With --cases, script IDs "<case id>--p<n>" (the paths command) resolve to
bank case <id>. Writes into --out (must not exist): cases/ (a bank), script.jsonl,
run/ (agent-eval artifacts), rows.jsonl and rejects.jsonl. Extra agent-eval
flags (a different --profile or --wire) go after `--`.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

from . import bank, jsonl, script

# The workbank arm of .claude/skills/rwkv-bench/sweep.py: catalog, file tools,
# budgets and wire. Sampling flags are omitted because a script ignores them.
BENCH_FLAGS = [
    "--tool-catalog", "work-v1", "--file-tools", "lines",
    "--max-steps", "16", "--max-tokens", "4096", "--decision-max-tokens", "2048",
    "--profile", "g1k", "--strict-spec",
    "--trace-prompt-bytes", "-1",
]


def add_arguments(parser) -> None:
    parser.add_argument("--records", type=Path, help="normalized records JSONL")
    parser.add_argument("--cases", type=Path, help="bank directory the --script case IDs resolve against")
    parser.add_argument("--script", type=Path, help="replay script (paths command output)")
    parser.add_argument("--out", type=Path, required=True, help="new output directory")
    parser.add_argument("--cli", type=Path, default=bank.REPO / "bin" / "rwkv-cli")
    parser.add_argument("--tracecorpus", type=Path, default=bank.REPO / "bin" / "tracecorpus")
    parser.add_argument("--parallelism", type=int, default=32)
    parser.add_argument("--allow-test-bank", action="store_true",
                        help="permit --cases inside bench/workbank (pipeline smoke tests; never train on the output)")
    parser.add_argument("--keep-failing", action="store_true",
                        help="also emit rows whose teacher trajectory fails the case expectations")
    parser.add_argument("extra", nargs="*", help="extra agent-eval flags after --")


def run(args) -> int:
    if bool(args.records) == bool(args.cases or args.script) or bool(args.cases) != bool(args.script):
        args.error("give either --records, or both --cases and --script")
    if args.cases and bank.is_test_bank(args.cases) and not args.allow_test_bank:
        args.error(f"--cases {args.cases} is the test bank; distill from a separate bank "
                   "(pass --allow-test-bank only for a smoke test)")

    if args.records:
        records = jsonl.read(args.records)
        cases = [bank.record_to_case(record) for record in records]
        entries = [bank.record_to_script(record) for record in records]
    else:
        entries = jsonl.read(args.script)
        cases = cases_for_script(bank.by_id(bank.load(args.cases)), entries)

    args.out.mkdir(parents=True, exist_ok=False)
    cases_path, script_path, run_dir = args.out / "cases", args.out / "script.jsonl", args.out / "run"
    bank.write(cases_path, cases)
    jsonl.write(script_path, entries)

    unloadable = set_aside_unloadable(args.cli, cases_path, args.out / "unloadable")
    for case_id, reason in unloadable:
        print(f"unloadable {case_id}: {reason}", file=sys.stderr)

    replay(args.cli, script_path, cases_path, run_dir, args.parallelism, args.extra)
    if not (run_dir / "trace.jsonl").is_file():
        print("agent-eval produced no trace", file=sys.stderr)
        return 1
    code = cut_rows(args.tracecorpus, run_dir, script_path, args.out, args.keep_failing)
    if unloadable:
        jsonl.write(args.out / "rejects.jsonl",
                    [{"case_id": case_id, "reason": "unloadable: " + reason} for case_id, reason in unloadable],
                    mode="a")
        print(f"  {len(unloadable):4d}  unloadable by the bank loader (see rejects.jsonl)")
    return code


def cases_for_script(cases: dict[str, dict], entries: list[dict]) -> list[dict]:
    """One case copy per script entry, renamed to the entry's ID."""
    resolved = []
    for item in entries:
        base = script.base_case_id(item["case_id"])
        if base not in cases:
            raise ValueError(f"script entry {item['case_id']} has no case {base}")
        resolved.append({**cases[base], "id": item["case_id"]})
    return resolved


def replay(cli: Path, script_path: Path, cases_path: Path, run_dir: Path, parallelism: int, extra: list[str]) -> None:
    command = [str(cli), "agent-eval", "--script", str(script_path), "--cases", str(cases_path),
               "--include-draft", "--case-parallelism", str(parallelism), "--output", str(run_dir),
               *BENCH_FLAGS, *extra]
    print("+", " ".join(command), file=sys.stderr)
    # agent-eval exits nonzero when cases fail; the teacher's failures are
    # reported by tracecorpus, so only a missing run directory is fatal.
    subprocess.run(command, cwd=bank.REPO)


def cut_rows(tracecorpus: Path, run_dir: Path, script_path: Path, out: Path, keep_failing: bool) -> int:
    command = [str(tracecorpus), "--run", str(run_dir), "--script", str(script_path),
               "--out", str(out / "rows.jsonl"), "--rejects", str(out / "rejects.jsonl")]
    if keep_failing:
        command.append("--require-pass=false")
    return subprocess.run(command, cwd=bank.REPO).returncode


_LOAD_ERROR = re.compile(r"cases/([^/]+)/case\.json: (.*)")


def set_aside_unloadable(cli: Path, cases_path: Path, parking: Path) -> list[tuple[str, str]]:
    """Move the cases the bank loader rejects out of cases_path until it loads.

    The loader enforces authoring rules (for example an expect.run script must
    ship in files) that some trajectories cannot meet without changing the
    workspace the teacher saw. The real validator decides; it stops at the
    first bad case, so probe until it loads (an empty script then fails the
    probe for a different reason, after loading).
    """
    rejected = []
    while True:
        probe = subprocess.run(
            [str(cli), "agent-eval", "--script", "/dev/null", "--cases", str(cases_path), "--include-draft",
             "--output", str(parking.parent / ".load-probe"), *BENCH_FLAGS],
            cwd=bank.REPO, capture_output=True, text=True)
        output = probe.stderr + probe.stdout
        match = _LOAD_ERROR.search(output)
        if not match or "load Agent eval cases" not in output:
            return rejected
        case_id, reason = match.group(1), match.group(2).strip()
        parking.mkdir(exist_ok=True)
        shutil.move(str(cases_path / case_id), str(parking / case_id))
        rejected.append((case_id, reason))

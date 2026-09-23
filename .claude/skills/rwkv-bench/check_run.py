#!/usr/bin/env python3
"""check_run.py — validity gate for one agent-eval run (docs/evaluations/benchmark-protocol.md §6).

Usage:
  check_run.py RUN_DIR --arm t03 [--rwkv] [--cases N] [--max-steps 16] [--max-tokens 4096]

Prints PASS/FAIL per gate and a strict score (invalid cases count as failures).
Exit status is 1 when any gate fails. Standard library only.
"""
import argparse
import json
import sys
from pathlib import Path

ARMS = {
    "greedy": dict(temperature=1, top_k=1, top_p=1, presence_penalty=0, frequency_penalty=0, penalty_decay=1),
    "t03": dict(temperature=0.3, top_k=65536, top_p=1, presence_penalty=0, frequency_penalty=0, penalty_decay=1),
    "backend": dict(temperature=1.0, top_k=20, top_p=0.3, presence_penalty=2.0, frequency_penalty=0.2, penalty_decay=0.996),
    "backend-nopen": dict(temperature=1.0, top_k=20, top_p=0.3, presence_penalty=0, frequency_penalty=0, penalty_decay=1),
}
# Sweep grid (docs/evaluations/g1k-sampling-sweep-20260923/PLAN.md): t<T*10>-p<top_p*10>, no truncation, no penalty.
for _t in (0.3, 0.6, 1.0):
    for _p in (1.0, 0.5):
        ARMS["t%02d-p%02d" % (round(_t * 10), round(_p * 10))] = dict(
            temperature=_t, top_k=65536, top_p=_p, presence_penalty=0, frequency_penalty=0, penalty_decay=1)
# API providers drop these fields; they are not part of the arm there.
API_UNSUPPORTED = {"top_k", "penalty_decay"}


def close(a, b):
    return a is not None and abs(float(a) - float(b)) < 1e-4


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir", type=Path)
    ap.add_argument("--arm", required=True, choices=sorted(ARMS))
    ap.add_argument("--rwkv", action="store_true", help="RWKV run: require wire_preset g1k")
    ap.add_argument("--primitive", action="store_true", help="Primitive suite: skip the g1k wire gate")
    ap.add_argument("--cases", type=int, help="expected case count")
    ap.add_argument("--max-steps", type=int, default=16)
    ap.add_argument("--max-tokens", type=int, default=4096)
    ap.add_argument("--decision-max-tokens", type=int, default=2048)
    ap.add_argument("--case-timeout-seconds", type=int, default=1800)
    args = ap.parse_args()

    run = json.loads((args.run_dir / "run.json").read_text(encoding="utf-8"))
    summary = json.loads((args.run_dir / "summary.json").read_text(encoding="utf-8"))
    harness, model, sampling = run.get("harness") or {}, run.get("model") or {}, run.get("sampling") or {}
    failures = []

    def gate(name, ok, detail=""):
        print(("PASS " if ok else "FAIL ") + name + (f"  ({detail})" if detail else ""))
        if not ok:
            failures.append(name)

    if args.rwkv and not args.primitive:
        gate("wire_preset == g1k", harness.get("wire_preset") == "g1k",
             f"wire_preset={harness.get('wire_preset')!r}")
    if not args.rwkv:
        gate("completion == chat-completions", model.get("completion") == "chat-completions",
             f"completion={model.get('completion')!r}")

    want = ARMS[args.arm]
    for key, value in want.items():
        if not args.rwkv and key in API_UNSUPPORTED:
            continue
        got = sampling.get(key)
        gate(f"sampling.{key} == {value}", close(got, value), f"got {got!r}")

    # Primitive suites own their step budget (per-case max_turns) and give the decision step a
    # full generation for multi-line tool arguments (eval.resolveCaseOptions); both are the
    # same for every arm, so they are reported, not gated.
    if args.primitive:
        print(f"SKIP max_steps / decision_max_output_tokens (suite-owned: "
              f"{harness.get('max_steps')!r} / {harness.get('decision_max_output_tokens')!r})")
    else:
        gate(f"max_steps == {args.max_steps}", harness.get("max_steps") == args.max_steps,
             f"got {harness.get('max_steps')!r}")
    answer_tokens = harness.get("answer_max_output_tokens")
    gate(f"answer_max_output_tokens == {args.max_tokens}", answer_tokens == args.max_tokens,
         f"got {answer_tokens!r}")

    decision_tokens = harness.get("decision_max_output_tokens")
    if not args.primitive:
        gate(f"decision_max_output_tokens == {args.decision_max_tokens}",
             decision_tokens == args.decision_max_tokens, f"got {decision_tokens!r}")

    timeout = harness.get("case_timeout_seconds")
    gate(f"case_timeout_seconds == {args.case_timeout_seconds}", timeout == args.case_timeout_seconds,
         f"got {timeout!r} (absent before 2026-09-23 binaries)")
    if args.rwkv:
        # A coalesced batch releases results only when its slowest member ends.
        wait = harness.get("remote_batch_wait_ms")
        gate("remote_batch_wait_ms == 0", wait == 0, f"got {wait!r}")

    case_ids = run.get("case_ids") or []
    if args.cases is not None:
        gate(f"case count == {args.cases}", len(case_ids) == args.cases, f"got {len(case_ids)}")

    metrics = summary.get("metrics") or {}
    task = metrics.get("task_success") or {}
    invalid = metrics.get("invalid_cases") or 0
    correct = task.get("correct", 0)
    strict_total = len(case_ids) or task.get("total", 0)
    print()
    print(f"model      {model.get('identifier')}  ({model.get('completion')})")
    print(f"official   {correct}/{task.get('total')}  (invalid excluded from denominator)")
    print(f"strict     {correct}/{strict_total} = {correct / strict_total:.1%}  (invalid counted as failures)"
          if strict_total else "strict     n/a")
    print(f"invalid    {invalid}  — transport errors must be re-run and merged before scoring")
    if failures:
        print(f"\nINVALID RUN: {len(failures)} gate(s) failed")
        return 1
    print("\nrun passes the validity gate")
    return 0


if __name__ == "__main__":
    sys.exit(main())

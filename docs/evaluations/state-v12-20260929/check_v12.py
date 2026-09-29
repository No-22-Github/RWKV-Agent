#!/usr/bin/env python3
"""Validity check for one v1.2 arm directory (see HANDOFF.md §4.1).

usage: check_v12.py <arm_dir> [--expect-state <state_id>]

Exit 0 only when both suites of the arm are usable for model comparison.
Do not relax these checks: every one of them was violated by a run that the
sweep gate marked PASS on 2026-09-29.
"""
import glob
import json
import os
import sys

SUITES = {"workbank": 148, "bfclp": 60}
MAX_INVALID = 3          # transport-invalid cases tolerated per run, counted as failures
MIN_ELAPSED = 120        # seconds; a real run of either suite takes several minutes


def fail(msg):
    print("INVALID", msg)
    return False


def check_run(run_dir, suite, expect_state):
    name = os.path.basename(run_dir)
    exp_path = os.path.join(run_dir, "experiment.json")
    sum_path = os.path.join(run_dir, "summary.json")
    if not (os.path.exists(exp_path) and os.path.exists(sum_path)):
        return fail(f"{name}: missing experiment.json or summary.json (run did not finish)")
    exp = json.load(open(exp_path))
    metrics = json.load(open(sum_path))["metrics"]
    errors = exp.get("infrastructure_errors") or []
    ok = True
    if any("uploaded state not found" in e for e in errors):
        ok = fail(f"{name}: state missing on endpoint ('uploaded state not found')")
    if exp.get("state_id", "") != expect_state:
        ok = fail(f"{name}: state_id {exp.get('state_id')!r} != expected {expect_state!r}")
    if not exp.get("gate_passed"):
        ok = fail(f"{name}: sweep gate failed")
    if exp["strict"]["total"] != SUITES[suite]:
        ok = fail(f"{name}: case count {exp['strict']['total']} != {SUITES[suite]}")
    invalid = metrics.get("invalid_cases", 0)
    if invalid > MAX_INVALID:
        ok = fail(f"{name}: {invalid} invalid cases (> {MAX_INVALID}); first error: {errors[0][:160] if errors else '-'}")
    if exp.get("elapsed_seconds", 0) < MIN_ELAPSED:
        ok = fail(f"{name}: finished in {exp.get('elapsed_seconds', 0):.0f}s (< {MIN_ELAPSED}s), not a real run")
    if ok:
        tag = "OK" if exp.get("valid_for_model_comparison") else f"OK-with-{invalid}-invalid"
        print(f"{tag} {name}: strict {exp['strict']['correct']}/{exp['strict']['total']}")
    return ok


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    arm_dir = args[0].rstrip("/")
    arm = os.path.basename(arm_dir)
    if "--expect-state" in args:
        expect_state = args[args.index("--expect-state") + 1]
    else:
        expect_state = "" if arm == "none" else ("t927-s316.pth" if arm == "t927" else arm + ".pth")
    ok = True
    for suite in SUITES:
        runs = sorted(glob.glob(os.path.join(arm_dir, f"{arm}-{suite}-g1k-agent-k*")))
        runs = [r for r in runs if os.path.isdir(r)]
        if not runs:
            ok = fail(f"{arm}: no {suite} run directory")
            continue
        for run in runs:
            ok = check_run(run, suite, expect_state) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

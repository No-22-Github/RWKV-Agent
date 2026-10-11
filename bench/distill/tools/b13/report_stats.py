"""Recompute b13 acceptance and before/after with the existing v1.4 counter.

python3 bench/distill/tools/b13/report_stats.py --json local/runs/distill/v141/b13/stats.json
"""
import argparse
import collections
import contextlib
import hashlib
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import v14_composition as composition
from distill_paths import REPO


def readrows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def count(extra=()):
    old_sources, old_args = composition.SOURCES, sys.argv
    try:
        composition.SOURCES = old_sources + list(map(str, extra))
        sys.argv = ["v14_composition.py"]
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            composition.main()
        return json.loads(out.getvalue())
    finally:
        composition.SOURCES, sys.argv = old_sources, old_args


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path)
    args = ap.parse_args()
    root = Path(REPO)
    run = root / "local/runs/distill/v141/b13"
    cases = {c["id"]: c for p in (run / "cases").glob("*/*/case.json") for c in [json.loads(p.read_text())]}
    initial_cases = {c["id"]: c for p in (run / "cases-v1").glob("*/*/case.json") for c in [json.loads(p.read_text())]}
    extras = {json.loads(p.read_text())["id"] for p in (run / "extra-cases").glob("*/*/case.json")}
    summaries = [json.loads((run / f"teacher-k{k}/summary.json").read_text()) for k in range(3)]
    revised = {cid for cid, c in cases.items() if c["tags"]["version"] > 1 and cid not in extras}
    revised_all = {json.loads(p.read_text())["id"] for p in (run / "fix-cases").glob("*/*/case.json")}
    fixed = [json.loads((run / f"fix-k{k}/summary.json").read_text()) for k in range(3)] if revised else []
    extra_runs = [json.loads((run / f"extra-k{k}/summary.json").read_text()) for k in range(3)] if extras else []
    extra_fixed_ids = {p.parent.name for p in (run / "extra-fix-cases").glob("*/*/case.json")}
    extra_fixed_runs = [json.loads((run / f"extra-fix-k{k}/summary.json").read_text()) for k in range(3)] if extra_fixed_ids else []
    def passk(runs, ids):
        results = [{c["id"]: c["passed"] for c in s["cases"]} for s in runs]
        counts = collections.Counter(sum(r.get(cid, False) for r in results) for cid in ids)
        return {f"{k}/3": counts[k] for k in (3, 2, 1, 0)}
    final_pass = collections.Counter()
    for cid in cases:
        runs = extra_fixed_runs if cid in extra_fixed_ids else extra_runs if cid in extras else fixed if cid in revised else summaries
        final_pass[sum(next(c["passed"] for c in s["cases"] if c["id"] == cid) for s in runs)] += 1
    rows_path = run / "corpus/rows.jsonl"
    rows = readrows(rows_path)
    ex = {e["case_id"] for e in readrows(root / "bench/distill/common/exclude.jsonl") if e.get("batch") in (None, "", "b13")}
    kept = [r for r in rows if r["meta"]["case_id"] not in ex]
    calls = collections.Counter(t for r in kept for t in r["meta"]["traj"]["tool_seq"])
    t1 = [r for r in kept if r["meta"]["turn"] == 1]
    paths = readrows(root / "bench/distill/v1.4/teacher/b13.jsonl")
    reports = readrows(run / "paths-report.jsonl")
    drops = collections.Counter()
    for p in reports:
        drops.update(p.get("drops", {}))
    out = {
        "cases_drafted": len(initial_cases)+len(extras), "cases": len(cases), "pass_original": passk(summaries, initial_cases),
        "pass_final_live": {f"{k}/3": final_pass[k] for k in (3, 2, 1, 0)},
        "extra_cases": sorted(extras), "pass_extra": passk(extra_runs, extras) if extras else {},
        "extra_fixed_cases": sorted(extra_fixed_ids), "pass_extra_fixed": passk(extra_fixed_runs, extra_fixed_ids) if extra_fixed_ids else {},
        "shelved": sorted(set(initial_cases) - set(cases)), "pass_original_live": passk(summaries, set(cases)&set(initial_cases)),
        "revised": sorted(revised), "pass_revised": passk(fixed, revised_all) if revised else {},
        "pass_revised_live": passk(fixed, revised) if revised else {},
        "paths": len(paths), "drops": dict(drops), "rows_rendered": len(rows), "rows_kept": len(kept),
        "cases_with_kept_rows": len({r["meta"]["case_id"].split("--")[0] for r in kept}),
        "excluded_paths": sorted({p["case_id"] for p in paths} & ex),
        "batch_first_turns": len(t1), "batch_zero_call_turn1": sum(r["meta"]["traj"]["zero_call"] for r in t1),
        "batch_multiturn_rows": sum(r["meta"]["traj"]["turns_total"] >= 2 for r in kept),
        "batch_calls": dict(calls),
        "batch_first_list_files": sum(bool(r["meta"]["traj"]["tool_seq"]) and r["meta"]["traj"]["tool_seq"][0] == "list_files" for r in t1),
        "tokens_max": max(r["meta"]["traj"]["tokens"] for r in kept),
        "wire_hash": sorted({r["meta"]["wire_hash"] for r in kept}),
        "cli_sha256": hashlib.sha256((root / "local/bin/rwkv-cli").read_bytes()).hexdigest(),
        "script_sha256": hashlib.sha256((root / "bench/distill/v1.4/teacher/b13.jsonl").read_bytes()).hexdigest(),
        "before": count(), "after": count([rows_path]),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    if args.json:
        args.json.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()

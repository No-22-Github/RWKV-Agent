#!/usr/bin/env python3
"""compare.py — compare two workbank runs or configs case by case.

Usage:
  compare.py <run_dir_A> <run_dir_B>      two run directories (summary.json+run.json)
  compare.py <config_name_A> <config_name_B>   two config names in ledger/cases.jsonl

For each argument a per-case pass value is built: 1.0/0.0 for run dirs, the
mean over k replicas for config names. Cases are aligned by case_id and the
report contains:
  - the flip list (A passed & B failed, A failed & B passed) with trace refs
  - a bootstrap 95% CI of the pass-rate difference (A - B), resampling whole
    families (same-family variants are highly correlated; cases without a
    family each form their own group), 2000 replicates, seed 0.

Output: a JSON object followed by a human-readable summary. Stdlib only.
"""
import argparse
import json
import random
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
CASES_JSONL = TOOLS_DIR.parent / "ledger" / "cases.jsonl"
N_BOOT = 2000
BOOT_SEED = 0
PASS_THRESHOLD = 0.5


def read_jsonl(path):
    path = Path(path)
    if not path.is_file():
        return []
    rows = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            print("warning: %s:%d is not valid JSON, skipped" % (path, i), file=sys.stderr)
    return rows


def load_run_dir(run_dir):
    base = Path(run_dir)
    try:
        summary = json.loads((base / "summary.json").read_text(encoding="utf-8"))
        manifest = json.loads((base / "run.json").read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit("error: %s is not a run directory: %s" % (run_dir, exc))
    except json.JSONDecodeError as exc:
        raise SystemExit("error: invalid JSON in %s: %s" % (run_dir, exc))
    tags_by_id = {}
    for c in manifest.get("cases") or []:
        if isinstance(c, dict) and c.get("id") is not None:
            tags_by_id[c["id"]] = c.get("tags") or {}
    cases = {}
    for c in summary.get("cases") or []:
        if not isinstance(c, dict) or c.get("id") is None:
            continue
        cid = c["id"]
        tags = c.get("tags") if isinstance(c.get("tags"), dict) and c.get("tags") \
            else tags_by_id.get(cid) or {}
        cases[cid] = {
            "value": 1.0 if c.get("passed") else 0.0,
            "family": tags.get("family"),
            "level": tags.get("level"),
            "trace_ref": "%s#%s" % (run_dir, cid),
        }
    return cases


def load_config(config_name):
    rows = [r for r in read_jsonl(CASES_JSONL) if r.get("config_name") == config_name]
    if not rows:
        raise SystemExit("error: no ledger rows for config_name %r in %s" % (config_name, CASES_JSONL))
    cases = {}
    for r in rows:
        cid = r.get("case_id")
        if cid is None:
            continue
        d = cases.setdefault(cid, {"vals": [], "family": None, "level": None,
                                   "trace_ref": r.get("trace_ref")})
        d["vals"].append(1.0 if r.get("passed") else 0.0)
        if d["family"] is None and r.get("family"):
            d["family"] = r.get("family")
        if d["level"] is None and r.get("level"):
            d["level"] = r.get("level")
    for d in cases.values():
        d["value"] = sum(d["vals"]) / len(d["vals"])
    return cases


def load_side(arg):
    if Path(arg).is_dir():
        return load_run_dir(arg)
    return load_config(arg)


def bootstrap_ci(families, a_vals, b_vals, n_boot=N_BOOT, seed=BOOT_SEED):
    """Percentile CI of mean(a)-mean(b) resampling whole family groups."""
    rng = random.Random(seed)
    diffs = []
    n_fam = len(families)
    for _ in range(n_boot):
        a_sum = b_sum = n = 0
        for _ in range(n_fam):
            fam = families[rng.randrange(n_fam)]
            for i in fam:
                a_sum += a_vals[i]
                b_sum += b_vals[i]
                n += 1
        if n:
            diffs.append((a_sum - b_sum) / n)
    if not diffs:
        return None, None, 0.0
    diffs.sort()
    lo = diffs[int(0.025 * (len(diffs) - 1))]
    hi = diffs[int(round(0.975 * (len(diffs) - 1)))]
    point = sum(a_vals) / len(a_vals) - sum(b_vals) / len(b_vals)
    return lo, hi, point


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Compare two runs (directories) or two config names (ledger) case by case.")
    ap.add_argument("a", help="run dir A or config name A")
    ap.add_argument("b", help="run dir B or config name B")
    args = ap.parse_args(argv)

    a_cases = load_side(args.a)
    b_cases = load_side(args.b)
    common = sorted(set(a_cases) & set(b_cases))
    only_a = sorted(set(a_cases) - set(b_cases))
    only_b = sorted(set(b_cases) - set(a_cases))

    a_pass = [cid for cid in common if a_cases[cid]["value"] >= PASS_THRESHOLD]
    b_pass = [cid for cid in common if b_cases[cid]["value"] >= PASS_THRESHOLD]
    flips_a_pass_b_fail = [cid for cid in common
                           if a_cases[cid]["value"] >= PASS_THRESHOLD
                           and b_cases[cid]["value"] < PASS_THRESHOLD]
    flips_a_fail_b_pass = [cid for cid in common
                           if a_cases[cid]["value"] < PASS_THRESHOLD
                           and b_cases[cid]["value"] >= PASS_THRESHOLD]

    a_vals = [a_cases[cid]["value"] for cid in common]
    b_vals = [b_cases[cid]["value"] for cid in common]

    families = {}
    for i, cid in enumerate(common):
        fam = a_cases[cid]["family"] or b_cases[cid]["family"] or "__solo__:%s" % cid
        families.setdefault(fam, []).append(i)
    family_lists = list(families.values())
    lo, hi, point = bootstrap_ci(family_lists, a_vals, b_vals)

    def flip_entries(cids):
        return [{"case": cid,
                 "a_trace": a_cases[cid]["trace_ref"],
                 "b_trace": b_cases[cid]["trace_ref"]} for cid in cids]

    report = {
        "a": args.a,
        "b": args.b,
        "common_cases": len(common),
        "pass_rate": {
            "a": round(sum(a_vals) / len(a_vals), 4) if a_vals else None,
            "b": round(sum(b_vals) / len(b_vals), 4) if b_vals else None,
            "diff_a_minus_b": round(point, 4) if a_vals and b_vals else None,
        },
        "bootstrap": {
            "unit": "family",
            "replicates": N_BOOT,
            "seed": BOOT_SEED,
            "families": len(family_lists),
            "ci95_a_minus_b": [None if lo is None else round(lo, 4),
                               None if hi is None else round(hi, 4)],
        },
        "flips": {
            "a_pass_b_fail": flip_entries(flips_a_pass_b_fail),
            "a_fail_b_pass": flip_entries(flips_a_fail_b_pass),
        },
        "only_in_a": only_a,
        "only_in_b": only_b,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))

    print()
    print("== %s vs %s ==" % (args.a, args.b))
    print("common cases: %d (only in A: %d, only in B: %d)"
          % (len(common), len(only_a), len(only_b)))
    if a_vals and b_vals:
        print("pass rate: A %.1f%%  B %.1f%%  diff (A-B) %+.1fpp"
              % (100 * sum(a_vals) / len(a_vals), 100 * sum(b_vals) / len(b_vals), 100 * point))
        print("bootstrap 95%% CI of diff (family resample, n=%d): [%+.1fpp, %+.1fpp]"
              % (N_BOOT, 100 * lo, 100 * hi))
    print("flips: A pass / B fail: %s" % (flips_a_pass_b_fail or "none"))
    print("flips: A fail / B pass: %s" % (flips_a_fail_b_pass or "none"))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Read-only joint allocation simulation; projected rows are NOT delivered rows.
Run from repository root: python3 bench/distill/tools/v141/plan.py --json <path>
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from b13.report_stats import count
import v14_composition as composition
from distill_paths import EXCLUDE_JSONL

KEYS = {
    "first": "zero_call_turn1", "tool_first": "first_action_list_files",
    "named_first": "first_action_list_files_when_prompt_names_path",
    "calls": "data_query_share_of_calls", "multi": "multi_turn_rows",
    "small": "catalog_le5_rows", "writes": "write_or_script_rows",
}


def fraction(s):
    return tuple(map(int, s.split(" ")[0].split("/")))


def simulate(baseline):
    z, first = fraction(baseline[KEYS["first"]])
    lf, tf = fraction(baseline[KEYS["tool_first"]])
    nlf, nf = fraction(baseline[KEYS["named_first"]])
    dq, calls = fraction(baseline[KEYS["calls"]])
    multi, rows = fraction(baseline[KEYS["multi"]])
    small, _ = fraction(baseline[KEYS["small"]])
    writes, _ = fraction(baseline[KEYS["writes"]])
    # Mutually exclusive row cohorts; behavior caps may overlap within a cohort.
    # Replacement retains row count and removes only redundant first list_files.
    budgets = [
        dict(name="replace_old_paths", rows=0, first=0, zero=0, tool_first=0,
             list_first=-350, named_first=0, named_list=-240, calls=-350,
             data_query=0, multi=0, small=0, writes=0),
        dict(name="b12_work_v2", rows=360, first=300, zero=30, tool_first=270,
             list_first=20, named_first=180, named_list=5, calls=900,
             data_query=0, multi=120, small=0, writes=75),
        dict(name="query_multiturn", rows=600, first=300, zero=0, tool_first=300,
             list_first=0, named_first=300, named_list=0, calls=800,
             data_query=600, multi=600, small=100, writes=60),
        dict(name="no_call_first_turn", rows=560, first=560, zero=560, tool_first=0,
             list_first=0, named_first=0, named_list=0, calls=0,
             data_query=0, multi=0, small=70, writes=0),
    ]
    base = dict(rows=rows, first=first, zero=z, tool_first=tf, list_first=lf,
                named_first=nf, named_list=nlf, calls=calls, data_query=dq,
                multi=multi, small=small, writes=writes)
    projected = {k: v + sum(b[k] for b in budgets) for k, v in base.items()}
    p = projected
    ratios = dict(zero_call_turn1=[p["zero"], p["first"]],
                  first_action_list_files=[p["list_first"], p["tool_first"]],
                  named_path_first_list_files=[p["named_list"], p["named_first"]],
                  data_query_share_of_calls=[p["data_query"], p["calls"]],
                  multi_turn_rows=[p["multi"], p["rows"]],
                  catalog_le5_rows=[p["small"], p["rows"]],
                  write_or_script_rows=[p["writes"], p["rows"]],
                  work_v2_rows=[360, p["rows"]])
    checks = dict(zero_22_to_28=.22 <= p["zero"] / p["first"] <= .28,
                  list_files_le40=p["list_first"] / p["tool_first"] <= .40,
                  named_list_files_le10=p["named_list"] / p["named_first"] <= .10,
                  data_query_ge10=p["data_query"] / p["calls"] >= .10,
                  multi_ge15=p["multi"] / p["rows"] >= .15,
                  small_ge7=p["small"] / p["rows"] >= .07,
                  writes_ge12=p["writes"] / p["rows"] >= .12)
    floors = dict(
        zero_only_first_rows=max(0, math.ceil((.22 * first - z) / .78)),
        non_list_tool_first_rows=max(0, math.ceil(lf / .4 - tf)),
        named_non_list_tool_first_rows=max(0, math.ceil(nlf / .1 - nf)),
        pure_query_calls=max(0, math.ceil((.1 * calls - dq) / .9)),
    )
    return dict(kind="conditional_plan_not_production", baseline=baseline,
                independent_floors_not_additive=floors, row_cohort_budgets=budgets,
                projected_counts=projected,
                projected_ratios={k: dict(numerator=a, denominator=b, percent=round(100*a/b, 3))
                                  for k, (a, b) in ratios.items()},
                projected_checks=checks,
                assumptions=["No source removal, family resplit or QA exclusion beyond baseline.",
                             "Replacement holds first-turn/row denominators fixed; no query lost.",
                             "All budgets describe retained replayed rows, not authored cases.",
                             "Call caps, same-file readback and natural negative behavior need real teacher QA.",
                             "Prioritize alternate existing paths; stop authoring when measured joint targets pass."])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path)
    ap.add_argument("--extra-rows", action="append", type=Path, default=[],
                    help="Additional completed batch renders; exclude rules still apply")
    args = ap.parse_args()
    extra = Path("local/runs/distill/v141/b13/corpus/rows.jsonl").resolve()
    sources = [extra, *[p.resolve() for p in args.extra_rows]]
    if len(set(map(str, [*composition.SOURCES, *sources]))) != len(composition.SOURCES) + len(sources):
        raise ValueError("duplicate row source")
    out = simulate(count(sources))
    out["input_sha256"] = {str(Path(p).relative_to(Path.cwd())):
        hashlib.sha256(Path(p).read_bytes()).hexdigest()
        for p in [*composition.SOURCES, *map(str, sources), EXCLUDE_JSONL]}
    rendered = json.dumps(out, ensure_ascii=False, indent=2) + "\n"
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()

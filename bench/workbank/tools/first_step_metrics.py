#!/usr/bin/env python3
"""First-step information-source metrics for the S1 source-hint experiment.

Usage:
  python3 first_step_metrics.py runs/workbank/closeout-v0-g1k runs/workbank/s1-srchint-g1k

Readout per the S1 proposal (first decision step only, greedy, deterministic):
first-step source correctness, web misuse on local cases, web usage on web
cases, first-step fabricated/absolute paths, step-1 structure closure, early
duplicates, answer-stage tool calls, and pass counts.
"""
import json
import pathlib
import re
import sys

LOCAL = {"list_files", "read_file", "read_lines", "search_text", "data_query",
         "fileedit", "write_file", "append_file", "replace_lines", "datetime", "calculator"}
WEB = {"web_search", "web_fetch"}
ABSPATH = re.compile(r"(/workspace|/home/|/Users/|\"path\"\s*:\s*\"/)")


def load(run):
    return {c["id"]: c for c in json.load(open(pathlib.Path(run) / "summary.json"))["cases"]}


def intended_tool(raw):
    match = re.search(r'"name"\s*:\s*"([a-z_]+)"', str(raw or ""))
    return match.group(1) if match else None


def metrics(cases):
    rows = {}
    for cid, case in cases.items():
        steps = case["turns"][0]["result"].get("steps", [])
        st = steps[0] if steps else {}
        parsed = st.get("action_type")
        intended = intended_tool(st.get("model_output"))
        pick = st.get("tool") if parsed == "tool" else None
        if pick is None and intended not in (None, "no_tool"):
            pick = intended
        is_web = cid.startswith("web-")
        is_nt = cid.startswith("nt-")
        if is_web:
            correct = pick in WEB
        elif is_nt:
            correct = pick is None
        else:
            correct = pick in LOCAL
        ever_web = any(s.get("tool") in WEB for t in case["turns"] for s in t["result"].get("steps", []))
        args1 = json.dumps(st.get("tool_arguments") or {})
        early_dup = any(
            (s.get("tool_result") or {}).get("ok") is False
            and "duplicate" in str((s.get("tool_result") or {}).get("error") or "")
            for t in case["turns"] for s in t["result"].get("steps", [])[:3]
        )
        answer_calls = sum(
            1 for t in case["turns"] for s in t["result"].get("steps", [])
            if s.get("stage") == "answer" and s.get("action_type") == "tool"
        )
        if parsed:
            broke = "parsed"
        elif intended not in (None, "no_tool"):
            broke = "envelope-broke"
        else:
            broke = "no-call-intent"
        rows[cid] = {
            "passed": str(case.get("passed")) == "True",
            "pick": pick or ("no_tool" if intended == "no_tool" else "-"),
            "correct": correct,
            "family": "web" if is_web else ("nt" if is_nt else "local"),
            "first_web": pick in WEB,
            "ever_web": ever_web,
            "abs_path": bool(ABSPATH.search(args1)),
            "step1": broke,
            "early_dup": early_dup,
            "answer_calls": answer_calls,
        }
    return rows


def summarize(name, rows):
    n = len(rows)
    pure_local = {c: r for c, r in rows.items() if r["family"] == "local" and not c.startswith("hyb-")}
    webs = {c: r for c, r in rows.items() if r["family"] == "web"}
    print(f"\n== {name} ==")
    print(f"passed: {sum(r['passed'] for r in rows.values())}/{n}")
    print(f"first-step correct (mechanical def): {sum(r['correct'] for r in rows.values())}/{n}")
    print(f"  web family first-step web: {sum(r['first_web'] for r in webs.values())}/{len(webs)}")
    print(f"  local+hyb first-step local: {sum(r['correct'] for c, r in rows.items() if r['family'] == 'local')}/32")
    print(f"pure-local (28) first-step web: {sum(r['first_web'] for r in pure_local.values())}/28")
    print(f"pure-local (28) ever-called-web: {sum(r['ever_web'] for r in pure_local.values())}/28")
    print(f"first-step abs/fabricated path: {sum(r['abs_path'] for r in rows.values())}")
    broke = [c for c, r in rows.items() if r["step1"] != "parsed"]
    print(f"step-1 unparsed: {len(broke)} ({', '.join(f'{c}:{rows[c]['step1']}' for c in sorted(broke)) or '-'})")
    print(f"early duplicate (steps 1-3): {sum(r['early_dup'] for r in rows.values())}")
    print(f"cases with answer-stage tool calls: {sum(1 for r in rows.values() if r['answer_calls'])}"
          f" ({sum(r['answer_calls'] for r in rows.values())} calls)")


def main():
    runs = [(pathlib.Path(p).name, metrics(load(p))) for p in sys.argv[1:]]
    for name, rows in runs:
        summarize(name, rows)
    if len(runs) >= 2:
        (n0, r0), (n1, r1) = runs[0], runs[1]
        flips = [c for c in r0 if r0[c]["passed"] != r1.get(c, {}).get("passed")]
        print(f"\n== {n0} -> {n1} ==")
        print(f"pass flips: {flips or 'none'}")
        moved = [c for c in r0 if r0[c]["pick"] != r1.get(c, {}).get("pick")]
        print(f"first-step pick changed ({len(moved)}): " + ", ".join(
            f"{c}:{r0[c]['pick']}->{r1[c]['pick']}" for c in sorted(moved)))


if __name__ == "__main__":
    main()

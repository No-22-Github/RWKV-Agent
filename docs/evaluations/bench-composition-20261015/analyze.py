#!/usr/bin/env python3
"""Recompute the tables in REPORT.md: bank composition and per-case pass rates.

Usage (from repo root):
    python3 docs/evaluations/bench-composition-20261015/analyze.py

Composition only reads bench/. Pass rates read local/runs/ (not in git), so they
reflect whatever runs exist on this machine.
"""
import collections as C
import glob
import json
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
TEACHER_MARKERS = ("deepseek", "minimax", "dsf", "m31f")

SUITES = {
    "workbank": "bench/workbank/cases/*/*/case.json",
    "p13-holdout": "bench/holdout/p13/*/*/case.json",
    "bashprobe-old": "bench/bashprobe/cases/*/case.json",
    "bashprobe-b14": "bench/bashprobe/cases-b14/*/case.json",
    "weatherprobe-old": "bench/weatherprobe/cases/*/case.json",
    "weatherprobe-b14": "bench/weatherprobe/cases-b14/*/case.json",
}


def zh(s):
    return bool(re.search(r"[一-鿿]", s))


def load(pattern):
    return [json.load(open(f)) for f in sorted(glob.glob(os.path.join(ROOT, pattern)))]


def answer_form(expect):
    if "expected_number" in expect:
        return "number"
    if expect.get("output_equals") == "UNKNOWN":
        return "abstain"
    if "output_equals" in expect or "output_equals_any" in expect:
        return "exact-string"
    if any(k.startswith("output_contains") for k in expect):
        return "contains"
    return "file-state-only"


def no_call_turn(t):
    e = t.get("expect", {})
    return e.get("tools") == [] or e.get("require_active_no_call") or e.get("max_calls") == 0


def composition():
    print("## composition")
    for name, pattern in SUITES.items():
        cs = load(pattern)
        print(
            f"{name:17} n={len(cs):3}"
            f" zh={sum(zh(c['turns'][0]['prompt']) for c in cs):3}"
            f" multi_user_msgs={sum(len(c['turns']) > 1 for c in cs):3}"
            f" no_call={sum(any(no_call_turn(t) for t in c['turns']) for c in cs):3}"
            f" file_state_only={sum(answer_form(c['turns'][-1].get('expect', {})) == 'file-state-only' for c in cs):3}"
        )
    wb = load(SUITES["workbank"])
    for label, key in [
        ("scenario", lambda c: [c["tags"]["scenario"]]),
        ("level", lambda c: [c["tags"]["level"]]),
        ("axes", lambda c: c["tags"].get("axes") or ["(none)"]),
        ("answer_form", lambda c: [answer_form(c["turns"][-1].get("expect", {}))]),
        ("ref_calls", lambda c: [c["tags"].get("ref_calls")]),
        ("author", lambda c: [c["tags"].get("author")]),
    ]:
        ctr = C.Counter(x for c in wb for x in key(c))
        print(f"workbank {label}:", ", ".join(f"{k}={v}" for k, v in sorted(ctr.items(), key=lambda kv: (-kv[1], str(kv[0])))))


def seeded():
    path = os.path.join(ROOT, "bench/workbank/seeded-base700.txt")
    return {l.strip() for l in open(path) if l.strip() and not l.startswith("#")}


def pass_rates():
    print("\n## workbank pass rates (local/runs, 148-case runs since 2026-10-03)")
    tags = {c["id"]: dict(c["tags"], form=answer_form(c["turns"][-1].get("expect", {}))) for c in load(SUITES["workbank"])}
    rwkv, teacher = [], []
    for f in glob.glob(os.path.join(ROOT, "local/runs/bench-2026*/**/summary.json"), recursive=True):
        rel = os.path.relpath(f, os.path.join(ROOT, "local/runs"))
        if "workbank" not in rel or "aborted" in rel or rel < "bench-20261003":
            continue
        cases = json.load(open(f))["cases"]
        if len(cases) != 148:
            continue
        (teacher if any(m in rel for m in TEACHER_MARKERS) else rwkv).append({c["id"]: bool(c["passed"]) for c in cases})
    print(f"runs: rwkv={len(rwkv)} teacher={len(teacher)}")
    if not rwkv:
        return
    rate = lambda runs, k: sum(r[k] for r in runs) / len(runs) if runs else float("nan")
    rows = [(k, t, rate(rwkv, k), rate(teacher, k)) for k, t in tags.items()]
    leak = seeded()
    for label, key in [
        ("scenario", lambda t: [t["scenario"]]),
        ("level", lambda t: [t["level"]]),
        ("answer_form", lambda t: [t["form"]]),
        ("axes", lambda t: t.get("axes") or ["(none)"]),
    ]:
        groups = C.defaultdict(list)
        for row in rows:
            for g in key(row[1]):
                groups[g].append(row)
        print(f"-- by {label}")
        for g, rs in sorted(groups.items(), key=lambda kv: -len(kv[1])):
            rw = [r[2] for r in rs]
            te = [r[3] for r in rs]
            print(f"   {str(g):16} n={len(rs):3} rwkv={sum(rw)/len(rw):.2f} teacher={sum(te)/len(te):.2f}"
                  f" never_passed={sum(x == 0 for x in rw):2} clean={sum(r[0] not in leak for r in rs):3}")
    rw = [r[2] for r in rows]
    print(f"never passed={sum(x == 0 for x in rw)} passed>=90%={sum(x >= 0.9 for x in rw)} in_between={sum(0 < x < 0.9 for x in rw)}")


if __name__ == "__main__":
    composition()
    pass_rates()

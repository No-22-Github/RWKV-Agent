#!/usr/bin/env python3
"""Backtest the quick exam against local run history (REPORT.md §9).

For every RWKV run that covers a source suite in full, compare the run's score
on the full exam's cases of that suite with its score on the quick exam's cases
of that suite, and report the Spearman rank correlation across runs. The quick
draw used the same history, so the figure is optimistic; it is a floor check,
not an unbiased estimate.

    python3 docs/evaluations/bench-composition-20261015/backtest_quick.py
"""
import glob
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def ranks(values):
    order = sorted(range(len(values)), key=lambda i: values[i])
    out = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        for k in range(i, j + 1):
            out[order[k]] = (i + j) / 2
        i = j + 1
    return out


def spearman(a, b):
    ra, rb = ranks(a), ranks(b)
    n = len(a)
    ma, mb = sum(ra) / n, sum(rb) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    va = sum((x - ma) ** 2 for x in ra) ** 0.5
    vb = sum((y - mb) ** 2 for y in rb) ** 0.5
    return cov / (va * vb) if va and vb else float("nan")


def main():
    full = json.load(open(os.path.join(ROOT, "bench/exam/full.json")))["cases"]
    quick = {c["id"] for c in json.load(open(os.path.join(ROOT, "bench/exam/quick.json")))["cases"]}
    by_suite = {}
    for c in full:
        by_suite.setdefault(c["suite"], set()).add(c["id"])
    rows = {}
    for path in glob.glob(os.path.join(ROOT, "local/runs/**/summary.json"), recursive=True):
        if "aborted" in path:
            continue
        run_json = os.path.join(os.path.dirname(path), "run.json")
        try:
            completion = json.load(open(run_json))["model"]["completion"]
            cases = {c["id"]: c["passed"] for c in json.load(open(path))["cases"]}
        except Exception:
            continue
        if not completion.startswith("rwkv"):
            continue
        for suite, ids in by_suite.items():
            if not ids <= set(cases):
                continue
            q = ids & quick
            if len(q) < 5:
                continue
            full_score = sum(cases[i] for i in ids) / len(ids)
            quick_score = sum(cases[i] for i in q) / len(q)
            rows.setdefault(suite, []).append((full_score, quick_score))
    for suite, pairs in sorted(rows.items()):
        if len(pairs) < 5:
            continue
        a, b = [p[0] for p in pairs], [p[1] for p in pairs]
        n_quick = len(by_suite[suite] & quick)
        print(f"{suite:16} runs={len(pairs):3}  quick cases={n_quick:2}/{len(by_suite[suite]):3}  spearman={spearman(a, b):.3f}")


if __name__ == "__main__":
    main()

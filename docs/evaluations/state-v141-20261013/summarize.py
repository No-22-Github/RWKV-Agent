#!/usr/bin/env python3
"""Score table for the v1.41 state bench (2026-10-13).

usage: summarize.py <runs_dir> [--k 0]
       summarize.py <runs_dir> --replicas 0,1,2 --pairs a:b,c:d

<runs_dir> holds <arm>-{workbank,bfclp,bashprobe}-g1k-agent-k<i>/summary.json
(test-1-41.sh). workbank is reported on the clean 112 (seeded-base700.txt
excluded) and on all 148; bfcl-product is split into Chinese and irrelevance;
bashprobe (work-v2) reports passes, cases that executed bash at least once,
and cases whose answer stage still emitted a tool call.
"""
import argparse
import glob
import json
import os
import re
from collections import Counter, defaultdict
from math import comb

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
ORDER = ["none", "v13b-s688"]


def seeded():
    path = os.path.join(REPO, "bench", "workbank", "seeded-base700.txt")
    return {l.strip() for l in open(path) if l.strip() and not l.startswith("#")}


def steps(case):
    for turn in case.get("turns") or []:
        yield from (turn.get("result") or {}).get("steps") or []


def arm_key(arm):
    if arm in ORDER:
        return (0, ORDER.index(arm), 0)
    m = re.match(r"v141([ab])-(fin|s(\d+))$", arm)
    if m:
        return (1, m.group(1), 10**6 if m.group(2) == "fin" else int(m.group(3)))
    return (2, arm, 0)


def sign_p(good, bad):
    n = good + bad
    if n == 0:
        return 1.0
    tail = sum(comb(n, i) for i in range(min(good, bad) + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def replicas(args, seeds):
    """Per arm and suite: score per replica, mean, range; then paired sign
    tests on per-case pass counts summed over the replicas present in both."""
    ks = args.replicas.split(",")
    scores = defaultdict(dict)  # (arm, suite) -> k -> score
    cases = defaultdict(dict)  # (arm, suite) -> k -> {id: passed}
    for path in glob.glob(os.path.join(args.runs_dir, "*-g1k-agent-k*/summary.json")):
        name = os.path.basename(os.path.dirname(path))
        m = re.match(r"(.+?)-(workbank|bfclp|bashprobe)-g1k-agent-k(\d+)$", name)
        if not m or m.group(3) not in ks:
            continue
        arm, suite, k = m.groups()
        got = json.load(open(path))["cases"]
        if suite == "workbank":
            got = [c for c in got if c["id"] not in seeds]
        cases[(arm, suite)][k] = {c["id"]: int(c["passed"]) for c in got}
        scores[(arm, suite)][k] = sum(c["passed"] for c in got)
    suites = [("workbank", "wb 干净 112"), ("bfclp", "bfclp 60"), ("bashprobe", "bashprobe 26")]
    arms = sorted({a for a, _ in scores}, key=arm_key)
    print("| arm | " + " | ".join("%s（各次 / 均值 / 极差）" % t for _, t in suites) + " |")
    print("|---|" + "---|" * len(suites))
    for arm in arms:
        cells = []
        for suite, _ in suites:
            got = scores.get((arm, suite), {})
            vals = [got[k] for k in ks if k in got]
            cells.append("%s / %.1f / %d" % (", ".join(map(str, vals)), sum(vals) / len(vals), max(vals) - min(vals))
                         if vals else "–")
        print("| %s | %s |" % (arm, " | ".join(cells)))
    if not args.pairs:
        return
    print()
    print("| 比较 | " + " | ".join("%s（好/差，p）" % t for _, t in suites) + " |")
    print("|---|" + "---|" * len(suites))
    for pair in args.pairs.split(","):
        a, b = pair.split(":")
        cells = []
        for suite, _ in suites:
            ka, kb = cases.get((a, suite), {}), cases.get((b, suite), {})
            common = [k for k in ks if k in ka and k in kb]
            if not common:
                cells.append("–")
                continue
            good = bad = 0
            for cid in ka[common[0]]:
                d = sum(ka[k].get(cid, 0) for k in common) - sum(kb[k].get(cid, 0) for k in common)
                good += d > 0
                bad += d < 0
            cells.append("%d / %d，%.2g（k=%d）" % (good, bad, sign_p(good, bad), len(common)))
        print("| %s vs %s | %s |" % (a, b, " | ".join(cells)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs_dir")
    ap.add_argument("--k", default="0")
    ap.add_argument("--replicas", help="comma-separated replica indices: per-arm mean/range table")
    ap.add_argument("--pairs", help="a:b,... paired sign tests (with --replicas)")
    args = ap.parse_args()
    seeds = seeded()
    if args.replicas:
        return replicas(args, seeds)
    table = {}
    for path in glob.glob(os.path.join(args.runs_dir, "*-g1k-agent-k%s/summary.json" % args.k)):
        name = os.path.basename(os.path.dirname(path))
        m = re.match(r"(.+?)-(workbank|bfclp|bashprobe)-g1k-agent-k\d+$", name)
        if not m:
            continue
        arm, suite = m.groups()
        cases = json.load(open(path))["cases"]
        row = table.setdefault(arm, {})
        if suite == "workbank":
            clean = [c for c in cases if c["id"] not in seeds]
            row["clean"] = (sum(c["passed"] for c in clean), len(clean))
            row["all"] = (sum(c["passed"] for c in cases), len(cases))
            row["wb_zero"] = sum((c.get("tool_calls") or 0) == 0 for c in cases)
        elif suite == "bfclp":
            by, tot = Counter(), Counter()
            for c in cases:
                group = "irr" if "irrelevance" in c.get("category", "") else "zh"
                tot[group] += 1
                by[group] += c["passed"]
            row["bfclp"] = (sum(c["passed"] for c in cases), len(cases))
            row["zh"] = (by["zh"], tot["zh"])
            row["irr"] = (by["irr"], tot["irr"])
        else:
            row["bash"] = (sum(c["passed"] for c in cases), len(cases))
            row["bash_used"] = sum(
                any(s.get("tool") == "bash" and s.get("tool_executed") for s in steps(c)) for c in cases)
            row["bash_late"] = sum(
                any(s.get("stage_violation") for s in steps(c)) for c in cases)

    def f(pair):
        return "%d/%d" % pair if pair else "–"

    print("| arm | wb 干净 112 | wb 148 | wb 零调用 | bfclp | 中文 | irrel | bashprobe | 用了 bash | 收尾吐调用 |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for arm in sorted(table, key=arm_key):
        r = table[arm]
        print("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            arm, f(r.get("clean")), f(r.get("all")), r.get("wb_zero", "–"),
            f(r.get("bfclp")), f(r.get("zh")), f(r.get("irr")),
            f(r.get("bash")), r.get("bash_used", "–"), r.get("bash_late", "–")))


if __name__ == "__main__":
    main()

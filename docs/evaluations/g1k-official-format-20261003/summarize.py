#!/usr/bin/env python3
"""Score table for the format ablation (2026-10-03).

usage: summarize.py <runs_dir> [--arms fA,fB,...]

<runs_dir> holds bench sweep output: <arm>-<suite>-g1k-agent-k<i>/summary.json.
workbank is reported on the clean 112 (bench/workbank/seeded-base700.txt
excluded) and on all 148; bfcl-product is split into its Chinese categories
(missing-required, multi-turn) and English irrelevance. It also links
<runs_dir>/_by_arm/<arm>/ so classify_failures.py from state-v12-20260929 can
read the same runs.
"""
import argparse
import glob
import json
import os
import re
from collections import Counter

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def seeded():
    path = os.path.join(REPO, "bench", "workbank", "seeded-base700.txt")
    return {l.strip() for l in open(path) if l.strip() and not l.startswith("#")}


def load(path):
    return json.load(open(path))["cases"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs_dir")
    ap.add_argument("--arms")
    args = ap.parse_args()
    seeds = seeded()
    runs = sorted(glob.glob(os.path.join(args.runs_dir, "*-*-g1k-agent-k*/summary.json")))
    table = {}
    for path in runs:
        name = os.path.basename(os.path.dirname(path))
        m = re.match(r"(.+?)-(workbank|bfclp)-g1k-agent-k(\d+)$", name)
        if not m:
            continue
        arm, suite, k = m.groups()
        if args.arms and arm not in args.arms.split(","):
            continue
        link = os.path.join(args.runs_dir, "_by_arm", arm)
        os.makedirs(link, exist_ok=True)
        target = os.path.join(link, name)
        if not os.path.lexists(target):
            os.symlink(os.path.abspath(os.path.dirname(path)), target)
        cases = load(path)
        row = table.setdefault((arm, k), {})
        calls = [c.get("tool_calls") or 0 for c in cases]
        row[suite + "_calls"] = sum(calls) / len(calls)
        row[suite + "_zero"] = sum(n == 0 for n in calls)
        if suite == "workbank":
            clean = [c for c in cases if c["id"] not in seeds]
            row["clean"] = (sum(c["passed"] for c in clean), len(clean))
            row["all"] = (sum(c["passed"] for c in cases), len(cases))
        else:
            by = Counter()
            tot = Counter()
            for c in cases:
                cat = c.get("category", "")
                group = "irrelevance" if "irrelevance" in cat else "zh"
                tot[group] += 1
                by[group] += c["passed"]
            row["bfclp"] = (sum(c["passed"] for c in cases), len(cases))
            row["bfclp_zh"] = (by["zh"], tot["zh"])
            row["bfclp_irr"] = (by["irrelevance"], tot["irrelevance"])

    def f(pair):
        return "%d/%d" % pair if pair else "–"

    print("| arm | k | wb clean | wb 148 | bfclp | 中文 | irrel | 合计 | wb 零调用 | wb 平均调用 |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for (arm, k), row in sorted(table.items()):
        total = (row.get("clean") or (0, 0))[0] + (row.get("bfclp") or (0, 0))[0]
        print("| %s | %s | %s | %s | %s | %s | %s | %d | %s | %s |" % (
            arm, k, f(row.get("clean")), f(row.get("all")), f(row.get("bfclp")),
            f(row.get("bfclp_zh")), f(row.get("bfclp_irr")), total,
            row.get("workbank_zero", "–"),
            "%.2f" % row["workbank_calls"] if "workbank_calls" in row else "–"))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Score table, paired flips and think diagnostics for the think-full retest (2026-10-10).

usage: summarize.py <runs_dir>

<runs_dir> holds <arm>-<suite>-k<i>/ run directories (arm A = g1k, T = g1k+think-full
with nudge=think). workbank is reported on all 148 and on the clean 112
(bench/workbank/seeded-base700.txt excluded); bfcl-product is split into Chinese
and English irrelevance. Paired flips compare per-case pass counts summed over
the k replicas. The think diagnostic classifies every model call whose output
opens a think block without closing it, by finish reason.
"""
import glob
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def seeded():
    path = os.path.join(REPO, "bench", "workbank", "seeded-base700.txt")
    return {l.strip() for l in open(path) if l.strip() and not l.startswith("#")}


def sign_test(plus, minus):
    n = plus + minus
    if n == 0:
        return 1.0
    k = min(plus, minus)
    p = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * p)


def think_stats(run_dir):
    stats = Counter()
    for line in open(os.path.join(run_dir, "trace.jsonl")):
        event = json.loads(line)
        if event.get("kind") != "model_call":
            continue
        call = event["model_call"]
        prompt = call.get("request", {}).get("prompt", "")
        text = (call.get("response") or {}).get("text") or ""
        stats["calls"] += 1
        full = text
        if prompt.endswith("<think"):
            full = "<think" + text
        if "<think" in full:
            stats["think"] += 1
            # Loop: some sentence of 30+ chars recurs 3+ times inside the think.
            body = full.split("</think>", 1)[0]
            sentences = Counter(s.strip() for s in re.split(r"[.\n。]", body) if len(s.strip()) >= 30)
            if sentences and max(sentences.values()) >= 3:
                stats["loop"] += 1
            if "</think>" not in full:
                # The backend reports finish_reason "stop" even at the token
                # cap, so classify by content: a real call emitted without
                # </think>; a quoted call template cut by the client stop; a
                # very long output that ran into the budget; the rest ended
                # early (EOS).
                if "<tool_call>" in text:
                    payload = text[text.rfind("<tool_call>") + len("<tool_call>"):].strip()
                    try:
                        call = json.loads(payload)
                        real = isinstance(call, dict) and call.get("name") not in (None, "", "TOOL_NAME", "...")
                    except ValueError:
                        real = False
                    stats["unclosed_realcall" if real else "unclosed_quote"] += 1
                elif len(text) >= 12000:
                    stats["unclosed_length"] += 1
                else:
                    stats["unclosed_eos"] += 1
    return stats


def main():
    runs_dir = sys.argv[1]
    seeds = seeded()
    rows = defaultdict(dict)
    passes = defaultdict(lambda: defaultdict(Counter))  # suite -> arm -> case -> passes
    thinks = defaultdict(Counter)
    for summary in sorted(glob.glob(os.path.join(runs_dir, "*-*-k*/summary.json"))):
        run_dir = os.path.dirname(summary)
        m = re.match(r"(\w+)-(workbank|bfclp)-k(\d+)$", os.path.basename(run_dir))
        if not m:
            continue
        arm, suite, k = m.groups()
        cases = json.load(open(summary))["cases"]
        row = rows[(arm, k)]
        for c in cases:
            passes[suite][arm][c["id"]] += int(c["passed"])
        if suite == "workbank":
            clean = [c for c in cases if c["id"] not in seeds]
            row["all"] = sum(c["passed"] for c in cases)
            row["clean"] = sum(c["passed"] for c in clean)
            calls = [c.get("tool_calls") or 0 for c in cases]
            row["zero"] = sum(n == 0 for n in calls)
            row["avg_calls"] = sum(calls) / len(calls)
        else:
            zh = [c for c in cases if "irrelevance" not in c.get("category", "")]
            irr = [c for c in cases if "irrelevance" in c.get("category", "")]
            row["bfclp"] = sum(c["passed"] for c in cases)
            row["zh"] = sum(c["passed"] for c in zh)
            row["irr"] = sum(c["passed"] for c in irr)
        thinks[(arm, suite)] += think_stats(run_dir)

    cols = ["all", "clean", "bfclp", "zh", "irr", "zero", "avg_calls"]
    print("| 组 | k | wb 148 | wb 干净 112 | bfclp 60 | 中文 40 | irrel 20 | wb 零调用 | wb 平均调用 |")
    print("|---|---|---|---|---|---|---|---|---|")
    for (arm, k), row in sorted(rows.items()):
        cells = [("%.2f" % row[c] if c == "avg_calls" else str(row[c])) if c in row else "–" for c in cols]
        print("| %s | %s | %s |" % (arm, k, " | ".join(cells)))

    print("\n| 组 | 指标 | 均值 | 极差 |")
    print("|---|---|---|---|")
    for arm in sorted({a for a, _ in rows}):
        for col in cols[:5]:
            vals = [rows[(a, k)][col] for (a, k) in rows if a == arm and col in rows[(a, k)]]
            if vals:
                print("| %s | %s | %.2f | %d–%d |" % (arm, col, sum(vals) / len(vals), min(vals), max(vals)))

    print("\n配对（逐题 k 次通过数之和，T 对 A）：")
    for suite, by_arm in passes.items():
        if "A" not in by_arm or "T" not in by_arm:
            continue
        ids = set(by_arm["A"]) | set(by_arm["T"])
        plus = sum(by_arm["T"][i] > by_arm["A"][i] for i in ids)
        minus = sum(by_arm["T"][i] < by_arm["A"][i] for i in ids)
        print("- %s：T 更好 %d 题、A 更好 %d 题，符号检验 p=%.3f" % (suite, plus, minus, sign_test(plus, minus)))
        better = sorted(i for i in ids if by_arm["T"][i] > by_arm["A"][i])
        worse = sorted(i for i in ids if by_arm["T"][i] < by_arm["A"][i])
        print("  - T+：%s" % ", ".join(better))
        print("  - T−：%s" % ", ".join(worse))

    print("\n| 组 | 套件 | 模型调用 | 含 think | think 复读(同句≥3 次) | 未闭合·写满预算(≥12k 字符) | 未闭合·没写 </think> 就发真实调用 | 未闭合·引用调用模板被停止串切断 | 未闭合·提前结束 |")
    print("|---|---|---|---|---|---|---|---|---|")
    for (arm, suite), s in sorted(thinks.items()):
        print("| %s | %s | %d | %d | %d | %d | %d | %d | %d |" % (
            arm, suite, s["calls"], s["think"], s["loop"], s["unclosed_length"],
            s["unclosed_realcall"], s["unclosed_quote"], s["unclosed_eos"]))


if __name__ == "__main__":
    main()

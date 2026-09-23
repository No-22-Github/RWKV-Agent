#!/usr/bin/env python3
"""rank.py — rank sampling arms from sweep.py runs using the pre-registered rules.

  rank.py runs/bench-20260923 [--prefix g1k] [--baseline greedy] [--floor 5] [--out rank.md]

Rules (docs/evaluations/g1k-sampling-sweep-20260923/PLAN.md):
  * only runs whose experiment.json has gate_passed=true count; strict score = correct / all cases
  * primary: workbank strict mean over replicas
  * stage 1 (k=1): rank by workbank + bfcl-product strict (combined)
  * floor: if every arm's workbank best <= --floor, workbank has no resolution; rank by combined
  * stage 2 (k>=2): rank by workbank mean; if #1 - #2 <= max(range #1, range #2) they are
    indistinguishable -> break by bfcl-product mean -> then by lower temperature
Paired flips vs --baseline use replica k0 on workbank, with a two-sided sign test.
Standard library only.
"""
import argparse
import json
import math
import re
from collections import defaultdict
from pathlib import Path

RUN = re.compile(r"^(?P<prefix>.+?)-(?P<suite>workbank|bfclp|boundary|assistant|smoke|porig30|pfb30)-(?P<arm>.+)-k(?P<k>\d+)$")


def load(out, prefix):
    runs = defaultdict(dict)  # (suite, arm) -> {k: record}
    for path in sorted(Path(out).iterdir()):
        m = RUN.match(path.name)
        if not path.is_dir() or not m or m["prefix"] != prefix:
            continue
        meta_path = path / "experiment.json"
        if not meta_path.is_file():
            continue
        meta = json.loads(meta_path.read_text())
        if meta.get("gate_passed") is not True:
            continue
        summary = json.loads((path / "summary.json").read_text())
        scores = {c["id"]: bool(c.get("passed")) and not c.get("invalid") for c in summary["cases"]}
        runs[(m["suite"], m["arm"])][int(m["k"])] = {
            "path": path, "meta": meta, "scores": scores,
            "correct": sum(scores.values()), "total": len(scores),
            "invalid": sum(1 for c in summary["cases"] if c.get("invalid")),
        }
    return runs


def stats(reps):
    values = [r["correct"] for _, r in sorted(reps.items())]
    if not values:
        return None
    return {"values": values, "mean": sum(values) / len(values), "range": max(values) - min(values),
            "total": next(iter(reps.values()))["total"], "k": len(values),
            "invalid": sum(r["invalid"] for r in reps.values()),
            "kept_with_errors": sum(1 for r in reps.values() if r["meta"].get("accepted_with_infra_errors"))}


def sign_test(plus, minus):
    n = plus + minus
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(0, min(plus, minus) + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def fmt(s):
    if not s:
        return "—"
    vals = "/".join(str(v) for v in s["values"])
    text = f"{s['mean']:.1f}/{s['total']}" if s["k"] > 1 else f"{vals}/{s['total']}"
    if s["k"] > 1:
        text += f" (k={s['k']}: {vals}, range {s['range']})"
    if s["invalid"]:
        text += f" ⚠ invalid {s['invalid']}"
    return text


def temperature(runs, arm):
    for (suite, a), reps in runs.items():
        if a == arm and reps:
            return next(iter(reps.values()))["meta"]["sampling"]["temperature"]
    return 99


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out", type=Path)
    ap.add_argument("--prefix", default="g1k")
    ap.add_argument("--baseline", default="greedy")
    ap.add_argument("--floor", type=int, default=5)
    ap.add_argument("--save", type=Path, help="also write the markdown here")
    args = ap.parse_args()

    runs = load(args.out, args.prefix)
    arms = sorted({arm for (_, arm) in runs})
    if not arms:
        raise SystemExit("no gated runs found")
    table = {arm: {"wb": stats(runs.get(("workbank", arm), {})),
                   "bp": stats(runs.get(("bfclp", arm), {}))} for arm in arms}
    lines = [f"# 采样扫描排名（{args.out}）", ""]

    wb_best = [max(t["wb"]["values"]) for t in table.values() if t["wb"]]
    floor = bool(wb_best) and max(wb_best) <= args.floor
    staged = [a for a in arms if table[a]["wb"] and table[a]["wb"]["k"] >= 2]
    stage = 2 if len(staged) >= 2 else 1

    def combined(arm):
        t = table[arm]
        return (t["wb"]["mean"] if t["wb"] else 0) + (t["bp"]["mean"] if t["bp"] else 0)

    if stage == 1 or floor:
        order = sorted(arms, key=lambda a: (-combined(a), temperature(runs, a)))
        rule = "综合分（workbank + bfcl-product）" + ("；**地板规则触发**：workbank 无区分度" if floor else "")
    else:
        pool = staged
        order = sorted(pool, key=lambda a: (-table[a]["wb"]["mean"], temperature(runs, a)))
        rule = "workbank 均值（k≥2 的档）"
        if len(order) >= 2:
            first, second = table[order[0]]["wb"], table[order[1]]["wb"]
            if first["mean"] - second["mean"] <= max(first["range"], second["range"]):
                bp = lambda a: table[a]["bp"]["mean"] if table[a]["bp"] else 0  # noqa: E731
                head = sorted(order[:2], key=lambda a: (-bp(a), temperature(runs, a)))
                order = head + order[2:]
                rule += f"；前两名差 {first['mean'] - second['mean']:.1f} ≤ 极差，视为无法区分 → 按 bfcl-product 均值，再按低温度"

    lines += [f"阶段 {stage}，排序依据：{rule}", "",
              "| # | 档 | workbank strict | bfcl-product strict | 综合 |", "|---|---|---|---|---|"]
    for i, arm in enumerate(order, 1):
        t = table[arm]
        lines.append(f"| {i} | `{arm}` | {fmt(t['wb'])} | {fmt(t['bp'])} | {combined(arm):.1f} |")
    others = [a for a in arms if a not in order]
    for arm in others:
        t = table[arm]
        lines.append(f"| – | `{arm}` | {fmt(t['wb'])} | {fmt(t['bp'])} | {combined(arm):.1f} |")

    base = runs.get(("workbank", args.baseline), {}).get(0)
    if base:
        lines += ["", f"## workbank 逐题配对（k0，对照 `{args.baseline}`）", "",
                  "| 档 | +翻正 | −翻负 | 符号检验 p |", "|---|---|---|---|"]
        for arm in order:
            other = runs.get(("workbank", arm), {}).get(0)
            if arm == args.baseline or not other:
                continue
            shared = base["scores"].keys() & other["scores"].keys()
            plus = sum(1 for c in shared if other["scores"][c] and not base["scores"][c])
            minus = sum(1 for c in shared if base["scores"][c] and not other["scores"][c])
            lines.append(f"| `{arm}` | +{plus} | −{minus} | {sign_test(plus, minus):.3f} |")

    kept = [a for a in arms if any(t and t["kept_with_errors"] for t in table[a].values())]
    if kept:
        lines += ["", "⚠ 这些档有 run 在最后一次尝试仍带基础设施错误，已按规程把作废计为失败保留：" +
                  ", ".join(f"`{a}`" for a in kept)]
    text = "\n".join(lines) + "\n"
    print(text)
    if args.save:
        args.save.write_text(text)


if __name__ == "__main__":
    main()

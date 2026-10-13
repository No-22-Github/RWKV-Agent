#!/usr/bin/env python3
"""Composition of the b14 cases, read from the written case.json files and specs.json.

    python3 bench/distill/tools/b14/stats.py [--json out.json]

Language: a case is Chinese when its prompts hold at least four CJK characters.
Multi-turn: more than one turn. First-turn zero-call: turn 1 sets tools: [] and
require_active_no_call.
"""
import argparse
import collections
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CASES = os.path.join(HERE, "..", "..", "v1.42", "cases")
NAMES = {"M9a": "跨文件聚合", "M9b": "批量编辑", "M9c": "长文件", "M9d": "缺命令恢复", "M9e": "该不该用 bash（负例）",
         "M9f": "cwd 不保留", "M9g": "精确匹配", "M10a": "直接天气/地标", "M10b": "天气写产物", "M10c": "复合请求",
         "M10d": "隐式需求/本地规则", "M10e": "概念负例", "M10f": "多轮换城市", "M10g": "查不到的地点"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    args = ap.parse_args()
    spec = json.load(open(os.path.join(HERE, "specs.json"), encoding="utf-8"))
    rows = []
    for path in sorted(glob.glob(os.path.join(CASES, "*", "*", "case.json"))):
        c = json.load(open(path, encoding="utf-8"))
        text = " ".join(t["prompt"] for t in c["turns"])
        first = c["turns"][0]["expect"]
        rows.append({"id": c["id"], "sub": spec[c["id"]]["sub"], "kind": spec[c["id"]]["kind"],
                     "zh": len(re.findall(r"[一-鿿]", text)) >= 4, "turns": len(c["turns"]),
                     "zero_first": first.get("tools") == [] and bool(first.get("require_active_no_call")),
                     "bytes": c["tags"]["fixture_bytes"], "weather": bool(c.get("weather_fixture"))})
    n = len(rows)
    by = collections.OrderedDict()
    for r in sorted(rows, key=lambda r: (r["sub"][:3], int(r["sub"][3:] if r["sub"][3:].isdigit() else 0), r["sub"])):
        b = by.setdefault(r["sub"], collections.Counter())
        b["cases"] += 1
        b["zh"] += r["zh"]
        b["multi"] += r["turns"] > 1
        b["zero"] += r["zero_first"]
    total = {"cases": n, "zh": sum(r["zh"] for r in rows), "multi": sum(r["turns"] > 1 for r in rows),
             "zero_first": sum(r["zero_first"] for r in rows), "turn_rows": sum(r["turns"] for r in rows),
             "bash": sum(not r["weather"] and r["sub"].startswith("M9") for r in rows), "weather_lane": sum(r["sub"].startswith("M10") for r in rows)}
    print("| 子类 | 名称 | 题数 | 中文 | 多轮 | 首轮零调用 |")
    print("|---|---|---:|---:|---:|---:|")
    for sub, b in by.items():
        print("| %s | %s | %d | %d | %d | %d |" % (sub, NAMES.get(sub, ""), b["cases"], b["zh"], b["multi"], b["zero"]))
    print("| 合计 | | %d | %d (%.1f%%) | %d (%.1f%%) | %d (%.1f%%) |" % (
        n, total["zh"], 100 * total["zh"] / n, total["multi"], 100 * total["multi"] / n, total["zero_first"], 100 * total["zero_first"] / n))
    print("\nturn rows (one per user turn): %d; bash lane %d, weather lane %d" % (total["turn_rows"], total["bash"], total["weather_lane"]))
    for lane, pre in (("bash", "M9"), ("weather", "M10")):
        sel = [r for r in rows if r["sub"].startswith(pre) and (pre == "M10" or not r["sub"].startswith("M10"))]
        print("%s: %d cases, zh %.1f%%, multi %.1f%%, zero-first %.1f%%" % (
            lane, len(sel), 100 * sum(r["zh"] for r in sel) / len(sel), 100 * sum(r["turns"] > 1 for r in sel) / len(sel),
            100 * sum(r["zero_first"] for r in sel) / len(sel)))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump({"total": total, "by_sub": {k: dict(v) for k, v in by.items()}, "cases": rows}, f, ensure_ascii=False, indent=1)
            f.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

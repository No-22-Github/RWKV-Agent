#!/usr/bin/env python3
"""Shape of g1k think-full trajectories, as a target for rendering thinking training data.

usage: python3 -I think_shape.py <runs_dir> [--groups T,F] [--examples N]

Reads <group>-<suite>-k<i>/summary.json (turns[].result.steps) and prints a
Markdown report: think length by stage and step position, language, opening
and closing phrasing, the bytes between the think and the action, the action
format, how often a think cites the previous tool result, and the shortest
passing trajectories verbatim (truncated). Read-only.

Conventions: the T/F prompts end with the withheld "<think", so model_output
starts with ">" that completes the tag. A think is "closed" when "</think>"
appears in the output. Token counts are estimated as chars / 3.5 (the backend
reports no usage); treat them as relative.
"""
import argparse
import glob
import json
import os
import re
import statistics
from collections import Counter, defaultdict

CJK = re.compile(r"[一-鿿]")
WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_./-]{2,}|\d+(?:\.\d+)?")


def quantiles(values):
    if not values:
        return "–"
    values = sorted(values)
    pick = lambda q: values[min(len(values) - 1, int(len(values) * q))]
    return "%d / %d / %d / %d" % (pick(0.1), pick(0.5), pick(0.9), values[-1])


def split_output(output):
    """Return (think, separator, action, closed) for one step output."""
    body = output[1:] if output.startswith(">") else output
    if body.lstrip().startswith("<think>"):
        body = body.lstrip()[len("<think>"):]
    if "</think>" not in body:
        return body, "", "", False
    think, rest = body.split("</think>", 1)
    action = rest.lstrip()
    separator = rest[: len(rest) - len(action)]
    return think, separator, action, True


def opening(think, words=4):
    tokens = think.strip().split()
    return " ".join(tokens[:words])


def closing(think):
    lines = [l.strip() for l in think.strip().splitlines() if l.strip()]
    if not lines:
        return ""
    last = re.split(r"(?<=[.!?。])\s+", lines[-1])[-1]
    return " ".join(last.split()[:4])


def cites_result(think, previous_result):
    """True when the think repeats a token that appeared in the previous tool
    result but not in the task prompt (file names, numbers, identifiers)."""
    if not previous_result:
        return None
    result_tokens = set(WORD.findall(previous_result))
    think_tokens = set(WORD.findall(think))
    noise = {"true", "false", "null", "result", "tool", "path", "content", "type", "file", "name"}
    return bool((result_tokens & think_tokens) - noise)


def load(runs_dir, groups):
    steps = []
    trajectories = []
    for summary in sorted(glob.glob(os.path.join(runs_dir, "*-*-k*/summary.json"))):
        run = os.path.basename(os.path.dirname(summary))
        match = re.match(r"(\w+)-(workbank|bfclp)-k(\d+)$", run)
        if not match or match.group(1) not in groups:
            continue
        group, suite, k = match.groups()
        for case in json.load(open(summary))["cases"]:
            for turn in case["turns"]:
                previous_result = ""
                turn_steps = []
                for index, step in enumerate(turn["result"]["steps"]):
                    output = step.get("model_output") or ""
                    think, separator, action, closed = split_output(output)
                    record = {
                        "group": group, "suite": suite, "run": run, "case": case["id"],
                        "passed": case["passed"], "stage": step.get("stage"), "position": index + 1,
                        "action_type": step.get("action_type") or "error", "tool": step.get("tool"),
                        "think": think, "separator": separator, "action": action, "closed": closed,
                        "previous_result": previous_result, "output": output,
                        "tool_result": str(step.get("tool_result") or ""),
                    }
                    steps.append(record)
                    turn_steps.append(record)
                    if step.get("tool_result"):
                        previous_result = str(step.get("tool_result"))
                trajectories.append({
                    "group": group, "suite": suite, "run": run, "case": case["id"],
                    "passed": case["passed"], "prompt": turn.get("prompt", ""),
                    "final": turn["result"].get("output", ""), "steps": turn_steps,
                })
    return steps, trajectories


def report(steps, trajectories, examples):
    out = []
    p = out.append
    groups = sorted({s["group"] for s in steps})
    p("## 1. 规模\n")
    p("| 组 | 套件 | 步数 | 闭合 | 闭合率 | 题次 | 通过题次 |")
    p("|---|---|---|---|---|---|---|")
    for g in groups:
        for suite in ("workbank", "bfclp"):
            sel = [s for s in steps if s["group"] == g and s["suite"] == suite]
            tr = [t for t in trajectories if t["group"] == g and t["suite"] == suite]
            if sel:
                closed = sum(s["closed"] for s in sel)
                p("| %s | %s | %d | %d | %.0f%% | %d | %d |" % (
                    g, suite, len(sel), closed, 100 * closed / len(sel), len(tr), sum(t["passed"] for t in tr)))

    p("\n## 2. 思考长度（闭合步，字符；p10 / p50 / p90 / max；约 3.5 字符 ≈ 1 token）\n")
    p("| 组 | 套件 | 阶段 | 位置 | 步数 | 通过题 | 失败题 |")
    p("|---|---|---|---|---|---|---|")
    for g in groups:
        for suite in ("workbank", "bfclp"):
            for stage in ("decision", "answer"):
                for label, test in (("首步", lambda s: s["position"] == 1), ("后续步", lambda s: s["position"] > 1)):
                    sel = [s for s in steps if s["group"] == g and s["suite"] == suite and s["stage"] == stage
                           and s["closed"] and test(s)]
                    if len(sel) < 3:
                        continue
                    passed = [len(s["think"]) for s in sel if s["passed"]]
                    failed = [len(s["think"]) for s in sel if not s["passed"]]
                    p("| %s | %s | %s | %s | %d | %s | %s |" % (g, suite, stage, label, len(sel), quantiles(passed), quantiles(failed)))

    p("\n## 3. 语言\n")
    p("| 组 | 套件 | 闭合步 | 思考以英文为主 | 思考以中文为主 | 动作/终答含中文 |")
    p("|---|---|---|---|---|---|")
    for g in groups:
        for suite in ("workbank", "bfclp"):
            sel = [s for s in steps if s["group"] == g and s["suite"] == suite and s["closed"]]
            if not sel:
                continue
            zh = sum(len(CJK.findall(s["think"])) > 0.2 * max(1, len(s["think"])) for s in sel)
            action_zh = sum(bool(CJK.search(s["action"])) for s in sel)
            p("| %s | %s | %d | %d | %d | %d |" % (g, suite, len(sel), len(sel) - zh, zh, action_zh))

    for g in groups:
        sel = [s for s in steps if s["group"] == g and s["closed"]]
        p("\n## 4. %s 组：开头与收尾措辞（闭合步，前 4 词）\n" % g)
        for label, test in (("首步", lambda s: s["position"] == 1), ("后续步", lambda s: s["position"] > 1)):
            part = [s for s in sel if test(s)]
            top = Counter(opening(s["think"]) for s in part).most_common(8)
            p("- %s开头（n=%d）：%s" % (label, len(part), "；".join("`%s` %d" % (k, v) for k, v in top)))
        top = Counter(closing(s["think"]) for s in sel).most_common(8)
        p("- 收尾句：%s" % "；".join("`%s` %d" % (k, v) for k, v in top))
        lead = Counter(repr(s["output"][:2]) for s in sel).most_common(4)
        p("- 输出开头两个字符（`>` 补全标签）：%s" % "；".join("%s %d" % (k, v) for k, v in lead))

    p("\n## 5. 思考与动作之间的格式\n")
    p("| 组 | 闭合步 | `</think>` 后分隔符 | 工具调用写法 | 终答（无调用）首字符 |")
    p("|---|---|---|---|---|")
    for g in groups:
        sel = [s for s in steps if s["group"] == g and s["closed"]]
        sep = Counter(repr(s["separator"]) for s in sel).most_common(3)
        calls = [s["action"] for s in sel if s["action"].startswith("<tool_call>")]
        style = Counter("换行" if c.startswith("<tool_call>\n") else "紧贴" for c in calls)
        finals = [s["action"] for s in sel if s["action"] and not s["action"].startswith("<tool_call>")]
        first = Counter(f[:1] for f in finals).most_common(3)
        p("| %s | %d | %s | %s | %s |" % (g, len(sel), "；".join("%s %d" % kv for kv in sep),
                                          "；".join("%s %d" % kv for kv in style.items()),
                                          "；".join("%r %d" % kv for kv in first)))

    p("\n## 6. 后续步是否引用上一步工具结果（闭合步，position>1）\n")
    p("| 组 | 套件 | 步数 | 引用了结果里的新 token | 通过题内 | 失败题内 |")
    p("|---|---|---|---|---|---|")
    for g in groups:
        for suite in ("workbank", "bfclp"):
            sel = [s for s in steps if s["group"] == g and s["suite"] == suite and s["closed"] and s["position"] > 1
                   and s["previous_result"]]
            if not sel:
                continue
            cite = [cites_result(s["think"], s["previous_result"]) for s in sel]
            ok = [c for s, c in zip(sel, cite) if s["passed"]]
            bad = [c for s, c in zip(sel, cite) if not s["passed"]]
            rate = lambda xs: "%d/%d" % (sum(xs), len(xs)) if xs else "–"
            p("| %s | %s | %d | %s | %s | %s |" % (g, suite, len(sel), rate(cite), rate(ok), rate(bad)))

    p("\n## 7. 每题的思考步数与轨迹长度（workbank）\n")
    p("| 组 | 结果 | 题次 | 步数 p50 / p90 | 整条轨迹思考字符 p50 / p90 |")
    p("|---|---|---|---|---|")
    for g in groups:
        for label, want in (("通过", True), ("失败", False)):
            tr = [t for t in trajectories if t["group"] == g and t["suite"] == "workbank" and t["passed"] == want]
            if not tr:
                continue
            n = sorted(len(t["steps"]) for t in tr)
            chars = sorted(sum(len(s["think"]) for s in t["steps"]) for t in tr)
            p("| %s | %s | %d | %d / %d | %d / %d |" % (g, label, len(tr), n[len(n) // 2], n[int(len(n) * 0.9)],
                                                     chars[len(chars) // 2], chars[int(len(chars) * 0.9)]))

    p("\n## 8. 通过轨迹原文（每组最短的 %d 条，workbank，全部闭合）\n" % examples)
    for g in groups:
        tr = [t for t in trajectories if t["group"] == g and t["suite"] == "workbank" and t["passed"]
              and all(s["closed"] for s in t["steps"]) and len(t["steps"]) >= 2]
        tr.sort(key=lambda t: sum(len(s["output"]) for s in t["steps"]))
        seen = set()
        shown = 0
        for t in tr:
            if t["case"] in seen or shown >= examples:
                continue
            seen.add(t["case"])
            shown += 1
            p("### %s · %s · %s\n" % (g, t["case"], t["run"]))
            p("```text")
            p("User: " + t["prompt"].strip()[:400])
            for s in t["steps"]:
                p("\nAssistant: <think" + s["output"][:1500])
                if s["tool_result"]:
                    p("\nUser: <tool_response>" + s["tool_result"][:300] + ("…" if len(s["tool_result"]) > 300 else "") + "</tool_response>")
            p("```\n")
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("runs_dir")
    parser.add_argument("--groups", default="T,F")
    parser.add_argument("--examples", type=int, default=3)
    args = parser.parse_args()
    steps, trajectories = load(args.runs_dir, set(args.groups.split(",")))
    print(report(steps, trajectories, args.examples))


if __name__ == "__main__":
    main()

"""Compare teacher thinking (API reasoning_content) with g1k think-full traces.

  python3 think_compare.py

Read-only. Reuses the measures of ../think-full-20261010/think_shape.py
(openings, closings, result citation, quantiles) so the numbers line up with
think-shape.md. bfcl is restricted to irrelevance + missing: DeepSeek's other
30 bfcl cases had to run with thinking disabled (tool_choice=required).
"""
import collections
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "think-full-20261010"))
from think_shape import CJK, closing, cites_result, opening, quantiles, split_output  # noqa: E402

RUNS = os.path.join(HERE, "..", "..", "..", "local", "runs")
GROUPS = {  # label -> (run glob, thinking source)
    "DeepSeek": ("bench-20261010-deepseek/dsf-{suite}-k0", "api"),
    "MiniMax": ("bench-20261010-minimax/m31f-{suite}-k0", "api"),
    "g1k-T": ("bench-20261010-thinkfull/T-{suite}-k[0-2]", "text"),
    "g1k-F": ("bench-20261010-thinkfull/F-{suite}-k[0-2]", "text"),
}
BFCL_KEEP = ("bfcl_irrelevance", "bfcl_missing_simple_python")
MARKERS = {
    "Wait/Hmm/Actually": re.compile(r"\b(Wait|Hmm|Actually|But wait)\b"),
    "We need / Let's": re.compile(r"\b(We need|Let's|We have|We should)\b"),
    "The user …": re.compile(r"\bThe user\b"),
    "Let me / I need": re.compile(r"\b(Let me|I need|I should|I will|I'll)\b"),
    "Markdown list/heading": re.compile(r"(?m)^\s*([-*] |\d+\. |#+ )"),
    "code / JSON in think": re.compile(r"```|\{\"|<tool_call>"),
}


def load(label, suite):
    pattern, source = GROUPS[label]
    steps, trajectories = [], []
    for run in sorted(glob.glob(os.path.join(RUNS, pattern.format(suite=suite)))):
        summary = os.path.join(run, "summary.json")
        if not os.path.exists(summary):
            continue
        for case in json.load(open(summary))["cases"]:
            if suite == "bfclp" and not case["id"].startswith(BFCL_KEEP):
                continue
            for turn in case["turns"]:
                previous, per_turn = "", []
                for index, step in enumerate(turn["result"].get("steps") or []):
                    if source == "api":
                        think, closed = step.get("reasoning_content") or "", True
                    else:
                        think, _, _, closed = split_output(step.get("model_output") or "")
                    record = {"case": case["id"], "passed": case["passed"], "position": index + 1,
                              "stage": step.get("stage"), "action": step.get("action_type") or "error",
                              "think": think.strip(), "closed": closed, "previous": previous,
                              "prompt": turn.get("prompt", "")}
                    steps.append(record)
                    per_turn.append(record)
                    if step.get("tool_result"):
                        previous = str(step["tool_result"])
                trajectories.append({"passed": case["passed"],
                                     "chars": sum(len(s["think"]) for s in per_turn), "steps": len(per_turn)})
    return steps, trajectories


def pct(a, b):
    return "%d/%d (%.0f%%)" % (a, b, 100.0 * a / b) if b else "–"


def main():
    for suite in ("workbank", "bfclp"):
        print("\n# %s%s\n" % (suite, "（irrelevance + missing，30 题/轮）" if suite == "bfclp" else ""))
        data = {label: load(label, suite) for label in GROUPS}
        print("| 组 | 步数 | 有思考的步 | 首步有思考 | 终答步有思考 | 首步长度 p10/p50/p90/max | 后续步长度 | 行数 p50 |")
        print("|---|---|---|---|---|---|---|---|")
        for label, (steps, _) in data.items():
            th = [s for s in steps if s["think"] and s["closed"]]
            first = [s for s in steps if s["position"] == 1]
            final = [s for s in steps if s["action"] == "final"]
            lines = sorted(len(s["think"].splitlines()) for s in th)
            print("| %s | %d | %s | %s | %s | %s | %s | %s |" % (
                label, len(steps), pct(len(th), len(steps)),
                pct(sum(1 for s in first if s["think"]), len(first)),
                pct(sum(1 for s in final if s["think"]), len(final)),
                quantiles([len(s["think"]) for s in th if s["position"] == 1]),
                quantiles([len(s["think"]) for s in th if s["position"] > 1]),
                lines[len(lines) // 2] if lines else "–"))
        print("\n| 组 | 引用上一步结果 | 中文为主（中文题内） | " + " | ".join(MARKERS) + " |")
        print("|---|---|---|" + "---|" * len(MARKERS))
        for label, (steps, _) in data.items():
            th = [s for s in steps if s["think"] and s["closed"]]
            later = [s for s in th if s["previous"]]
            cites = sum(1 for s in later if cites_result(s["think"], s["previous"]))
            zh_prompt = [s for s in th if CJK.search(s["prompt"])]
            zh_think = sum(1 for s in zh_prompt if len(CJK.findall(s["think"])) > 0.2 * len(s["think"]))
            marks = [pct(sum(1 for s in th if rx.search(s["think"])), len(th)) for rx in MARKERS.values()]
            print("| %s | %s | %s | %s |" % (label, pct(cites, len(later)), pct(zh_think, len(zh_prompt)), " | ".join(marks)))
        print("\n| 组 | 通过题整条思考 p50/p90（字符） | 失败题整条思考 p50/p90 |")
        print("|---|---|---|")
        for label, (_, trajs) in data.items():
            q = lambda xs: (lambda v: "%d / %d" % (v[len(v) // 2], v[int(len(v) * 0.9)]) if v else "–")(sorted(xs))
            print("| %s | %s | %s |" % (label, q([t["chars"] for t in trajs if t["passed"]]),
                                        q([t["chars"] for t in trajs if not t["passed"]])))
        for label, (steps, _) in data.items():
            th = [s for s in steps if s["think"] and s["closed"]]
            for name, pick in (("首步开头", lambda s: s["position"] == 1), ("后续步开头", lambda s: s["position"] > 1)):
                c = collections.Counter(opening(s["think"]) for s in th if pick(s))
                print("- %s %s：%s" % (label, name, "；".join("`%s` %d" % kv for kv in c.most_common(6))))
            c = collections.Counter(closing(s["think"]) for s in th)
            print("- %s 收尾：%s" % (label, "；".join("`%s` %d" % kv for kv in c.most_common(6))))


if __name__ == "__main__":
    main()

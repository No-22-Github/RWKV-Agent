#!/usr/bin/env python3
"""Checks on agent-eval teacher runs (v1.4 b10a): the b10_check.py form rules
applied to run outputs, plus the §3.6 thinking stats (methodology follows
docs/evaluations/deepseek-teacher-20261010/think_compare.py).  Read-only.

  python3 run_check.py --run local/runs/distill/v141/smoke/b10-suffix [--run ...] [--passed-only]
"""
import argparse
import collections
import json
import os
import re
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
from b10_check import check  # noqa: E402
from distill_paths import find_case  # noqa: E402

WAIT = re.compile(r"\b(Wait|Hmm|Actually|But wait)\b")
CJK = re.compile(r"[\u4e00-\u9fff]")


def quantiles(xs):
    if not xs:
        return "–"
    xs = sorted(xs)
    p = lambda q: xs[min(len(xs) - 1, int(len(xs) * q))]
    return "p50 %d / p90 %d / max %d" % (p(0.5), p(0.9), xs[-1])


def load(run):
    s = json.load(open(os.path.join(run, "summary.json")))
    for c in s["cases"]:
        steps = [st for t in c["turns"] for st in (t.get("result") or {}).get("steps") or []]
        yield c["id"], {
            "passed": bool(c.get("passed")),
            "outputs": [st.get("model_output") or "" for st in steps],
            "thinks": [st.get("reasoning_content") or "" for st in steps],
            "prompts": " ".join(t.get("prompt") or "" for t in c["turns"]),
        }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="append", required=True)
    ap.add_argument("--passed-only", action="store_true")
    args = ap.parse_args()
    form = collections.Counter()
    total_steps = with_think = over900 = wait = zh_think = 0
    zh_prompt_steps = []
    first_lens, later_lens = [], []
    problems_by_case = collections.defaultdict(list)
    for run in args.run:
        for cid, d in load(run):
            if args.passed_only and not d["passed"]:
                continue
            case = find_case(cid)
            for p in (check({"outputs": d["outputs"]}, case) if case else ["<case not found>"]):
                form[p.split(":")[0]] += 1
                problems_by_case[cid].append(p)
            for i, t in enumerate(d["thinks"]):
                total_steps += 1
                if not t:
                    continue
                with_think += 1
                first_lens.append(len(t)) if i == 0 else later_lens.append(len(t))
                over900 += len(t) > 900
                wait += bool(WAIT.search(t))
                if CJK.search(d["prompts"]):
                    zh = len(CJK.findall(t)) > 0.2 * len(t)
                    zh_prompt_steps.append(zh)
                    zh_think += zh
    print("runs: %s" % ", ".join(os.path.basename(r) for r in args.run))
    print("form problems:", dict(form) or "none")
    for cid, ps in sorted(problems_by_case.items()):
        print("   %s: %s" % (cid, "; ".join(ps)))
    print("thinking steps: %d/%d (%.0f%%)" % (with_think, total_steps, 100.0 * with_think / total_steps if total_steps else 0))
    print("first-step think len: %s" % quantiles(first_lens))
    print("later-step think len: %s" % quantiles(later_lens))
    print(">900 chars steps: %d/%d (%.0f%%)" % (over900, with_think, 100.0 * over900 / with_think if with_think else 0))
    print("Wait/Hmm/Actually: %d/%d (%.0f%%)" % (wait, with_think, 100.0 * wait / with_think if with_think else 0))
    print("Chinese-prompt think in Chinese: %d/%d" % (zh_think, len(zh_prompt_steps)))


if __name__ == "__main__":
    main()

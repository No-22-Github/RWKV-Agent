#!/usr/bin/env python3
"""Mechanical quality filter for a v2.0 replay script (corpus paths output).

    python3 bench/distill/tools/v22/filter.py --script T/paths.jsonl --cases T/cases \
        --out T/script.jsonl --report T/filter-report.json

The teacher ran without the 1.x suffix, so its known habits come back: long
Markdown answers, answering in the wrong language, very long deliberation. A
path is kept only when every check passes; nothing is patched except one normalization:

  scalar_args        Qwen spells every integer and boolean argument as a
                     string ("max_results":"10", "case_sensitive":"False").
                     The harness coerces them, so the paths passed, but the
                     student would learn quoted scalars. Fields the work-v2
                     schemas declare integer/boolean are rewritten to JSON
                     literals inside the tool call text (top-level arguments
                     of the named tool only; anything that does not parse
                     exactly stays as it is and is counted).

Checks:

  final_too_long     agent cases: a final answer > 600 chars
                     daily-QA (b20d): > 2500 chars; v2.1 long-text task types
                     (rewrite_text, draft_document, code_help, summarize_page): > 2000
  final_markdown     a turn asks for the value only and a final answer carries
                     Markdown (bold, code, bullets, tables). Elsewhere Markdown
                     is kept: the App renders it and a table or code block is
                     often the better answer (user decision 2026-10-14)
  final_language     first prompt Chinese and a final answer that is English
                     prose (no Chinese, 4+ English words; a bare value, path
                     or DONE is language-neutral), or prompt without Chinese
                     and a final answer mostly Chinese
  reasoning_too_long one step's reasoning > 3000 chars (daily-QA 5000), or a
                     path > 12000
  reasoning_meta     the reasoning talks about its own instructions or harness
                     ("system prompt", "the instructions say", "my rules",
                     "the example says", "test case", "verify") — the student
                     must not learn to recite rules it is never shown
  leaked_markup      a final answer carries <think>, </think> or <tool_call>
  reasoning_markup   a step's reasoning carries tool or think markup
                     (<tool_call>, <tool_code>, </function_code>, </think>...)
Steps without reasoning are counted (render replays them as an empty think
block) but do not drop the path.
"""
import argparse
import collections
import json
import os
import re

CJK = re.compile(r"[一-鿿]")
MD = re.compile(r"^\s*#{1,6} |\*\*[^*]+\*\*|^\s*\|.*\|\s*$|```|^\s*[-*] \S|`[^`]+`", re.M)
VALUE_ONLY = re.compile(r"只回答|只给|只输出|只说|仅回答|只要(数字|结果|答案|名字|值)|only the|just the|reply with only|answer with only", re.I)
META = re.compile(
    r"system (prompt|message|instruction)|developer (message|instruction)|the instructions? (say|says|tell|require)"
    r"|my (rules|instructions)|the rules? (say|says|require)|according to the (rules|instructions)"
    r"|the example (says|shows)|\btest case\b|\bverify\.py\b|\bthe grader\b|\bevaluat(or|ion) (expects|checks)",
    re.I)


# work-v3 schema: tool -> {argument: "int" | "bool"} (read_lines kept for
# work-v2 paths; work-v3 read_file takes the same range)
SCALAR_ARGS = {
    "list_files": {"max_depth": "int", "max_results": "int"},
    "search_text": {"max_results": "int", "case_sensitive": "bool"},
    "web_search": {"max_results": "int"},
    "get_weather": {"days": "int"},
    "calculator": {"precision": "int"},
    "read_lines": {"start_line": "int", "end_line": "int"},
    "read_file": {"start_line": "int", "end_line": "int"},
    "replace_lines": {"start_line": "int", "end_line": "int"},
}
CALL_NAME = re.compile(r'^\s*<tool_call>\{"name":"(\w+)"')
REASONING_MARKUP = re.compile(r"</?(think|tool_call|tool_code|tool_response|function_code|function_call)>")


def normalize_scalars(text, counts):
    """Rewrite string-spelled integer/boolean arguments to JSON literals."""
    m = CALL_NAME.match(text)
    fields = SCALAR_ARGS.get(m.group(1), {}) if m else {}
    for field, kind in fields.items():
        def literal(v):
            if kind == "int" and re.fullmatch(r"-?\d+", v.strip()):
                counts["scalar_args_fixed"] += 1
                return '"%s":%d' % (field, int(v.strip()))
            if kind == "bool" and v.strip().lower() in ("true", "false"):
                counts["scalar_args_fixed"] += 1
                return '"%s":%s' % (field, v.strip().lower())
            counts["scalar_args_left"] += 1
            return None
        text = re.sub(r'"%s":"([^"\\]*)"' % field,
                      lambda mm: literal(mm.group(1)) or mm.group(0), text)
    return text


def is_call(text):
    return text.lstrip().startswith("<tool_call>")


def zh_share(text):
    letters = [c for c in text if c.isalpha()]
    return sum(bool(CJK.match(c)) for c in letters) / max(len(letters), 1)


def load_cases(root):
    cases = {}
    for dirpath, _, files in os.walk(root):
        if "case.json" in files:
            case = json.load(open(os.path.join(dirpath, "case.json"), encoding="utf-8"))
            cases[case["id"]] = case
    return cases


LONG_TASKS = {"rewrite_text", "draft_document", "code_help", "summarize_page"}


def check(entry, case):
    reasons = []
    daily = case.get("tags", {}).get("batch") == "b20d"
    final_cap = 2500 if daily else 2000 if case.get("tags", {}).get("task_type") in LONG_TASKS else 600
    prompt_zh = bool(CJK.search(case["turns"][0]["prompt"]))
    value_only = any(VALUE_ONLY.search(t["prompt"]) for t in case["turns"])
    total = 0
    for out in entry["outputs"]:
        if not out.get("supervised", True):
            continue
        reasoning = (out.get("reasoning") or "").strip()
        total += len(reasoning)
        if len(reasoning) > (5000 if daily else 3000):
            reasons.append("reasoning_too_long")
        if META.search(reasoning):
            reasons.append("reasoning_meta")
        if REASONING_MARKUP.search(reasoning):
            reasons.append("reasoning_markup")
        text = out["text"]
        if is_call(text):
            continue
        if re.search(r"</?think>|<tool_call>", text):
            reasons.append("leaked_markup")
        if len(text) > final_cap:
            reasons.append("final_too_long")
        if value_only and MD.search(text):
            reasons.append("final_markdown")
        if prompt_zh and not CJK.search(text) and len(re.findall(r"[A-Za-z]{3,}", text)) >= 4:
            # a bare value, path or DONE is language-neutral; only prose counts
            reasons.append("final_language")
        if not prompt_zh and zh_share(text) > 0.5:
            reasons.append("final_language")
    if total > 12000:
        reasons.append("reasoning_too_long")
    return sorted(set(reasons))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--script", required=True)
    ap.add_argument("--cases", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--report", required=True)
    ap.add_argument("--exclude-ids", help="file of case ids rerun in another batch; their paths here are dropped as superseded")
    args = ap.parse_args()
    excluded = {l.strip() for l in open(args.exclude_ids) if l.strip()} if args.exclude_ids else set()
    cases = load_cases(args.cases)
    kept, drops, empty_steps, steps = [], collections.Counter(), 0, 0
    scalars = collections.Counter()
    per_case = []
    for line in open(args.script, encoding="utf-8"):
        entry = json.loads(line)
        base = re.sub(r"--p\d+$", "", entry["case_id"])
        reasons = ["superseded"] if base in excluded else check(entry, cases[base])
        for out in entry["outputs"]:
            if out.get("supervised", True):
                steps += 1
                empty_steps += not (out.get("reasoning") or "").strip()
        per_case.append({"case_id": entry["case_id"], "drop": reasons})
        if reasons:
            drops.update(reasons)
        else:
            for out in entry["outputs"]:
                out["text"] = normalize_scalars(out["text"], scalars)
            kept.append(json.dumps(entry, ensure_ascii=False) + "\n")
    with open(args.out, "x", encoding="utf-8") as f:
        f.writelines(kept)
    report = {"paths": len(per_case), "kept": len(kept), "drop_reasons": dict(drops.most_common()),
              "steps": steps, "steps_without_reasoning": empty_steps, **scalars, "cases": per_case}
    with open(args.report, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(json.dumps({k: v for k, v in report.items() if k != "cases"}, ensure_ascii=False))


if __name__ == "__main__":
    main()

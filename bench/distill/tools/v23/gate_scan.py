#!/usr/bin/env python3
"""v2.3 plan §4.4: trajectory-level quality gate over rendered rows.

    python3 bench/distill/tools/v23/gate_scan.py --out drop.tsv ROWS.jsonl [...]

Judging only looks at the final answer, so a teacher's wandering, copying or
"this is a simulated environment" still trains. Every trajectory (case#turn)
is checked over all of its rows; any hit drops the whole case (all turns).

  same_result     a read-only tool returns a result identical to an earlier one
                  (query ignored, no write in between) two or more times
  same_call       an identical call is re-sent with no write in between
  think_copy      a step's thinking repeats the previous step's (≥ 90% similar)
  env_aware       thinking or answer says the data is simulated/placeholder/test
  year_mismatch   a web_search query names a year before 2026 the user never did
  long_think      one step's thinking is longer than 900 characters
  flail           two or more steps whose thinking says the command was wrong
  forbidden_call  a tool call trained after the harness disabled tools
  no_think        a trained step has no <think> block (DeepSeek skips some)

Prints counts per reason and per source; --out writes "<source>\\t<case>#<turn>\\t<reasons>".
"""
import argparse
import ast
import collections
import difflib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scan_forbidden import bad as forbidden_call  # noqa: E402

READ_ONLY = {"read_file", "list_files", "search_text", "web_search", "web_fetch", "data_query",
             "datetime", "get_weather", "calculator"}
WRITES = {"write_file", "replace_lines", "append_file", "bash"}
CALL = re.compile(r"<tool_call>(\{.*?\})</tool_call>", re.S)
RESP = re.compile(r"<tool_response>(\{.*?\})</tool_response>", re.S)
THINK = re.compile(r"<think>(.*?)</think>", re.S)
URL = re.compile(r"https?://\S+|\b[\w.-]+\.example\b")
ENV = re.compile(r"模拟数据|模拟环境|示例域名|示例网址|占位|测试环境|虚构的?网站|placeholder|mock data|simulated "
                 r"(?:data|environment|site)|test environment|fixture|example domain|sandbox data", re.I)
FLAIL = re.compile(r"命令不对|命令有误|命令错|写法不对|换(?:个|一种|一个)写法|语法错|被截断|没有输出|报错了|"
                   r"didn't work|did not work|wrong command|syntax error|try (?:a )?different (?:approach|command)|"
                   r"command failed|was truncated", re.I)
YEAR = re.compile(r"\b(20[0-2]\d)\b")


def meta(row):
    m = row["meta"]
    return m if isinstance(m, dict) else ast.literal_eval(m)


def parse(js):
    try:
        return json.loads(js)
    except ValueError:
        return None


def strip_query(obj):
    if isinstance(obj, dict):
        return {k: strip_query(v) for k, v in obj.items() if k != "query"}
    if isinstance(obj, list):
        return [strip_query(v) for v in obj]
    return obj


def scan_turn(rows):
    """rows: one trajectory's rows sorted by step."""
    hits = set()
    last = rows[-1]["text"]
    user_text = last.split("\n\nAssistant:", 1)[0]
    calls = [parse(c) for c in CALL.findall(last)]
    resps = [parse(r) for r in RESP.findall(last)]
    seen_results, seen_calls, repeats = [], [], 0
    for call, resp in zip(calls, resps):
        if not call:
            continue
        name = call.get("name")
        if name in WRITES:
            seen_results, seen_calls = [], []
            continue
        key = json.dumps(call, sort_keys=True, ensure_ascii=False)
        if key in seen_calls:
            hits.add("same_call")
        seen_calls.append(key)
        if name in READ_ONLY and resp is not None:
            res = json.dumps(strip_query(resp), sort_keys=True, ensure_ascii=False)
            if res in seen_results:
                repeats += 1
            seen_results.append(res)
        if name == "web_search":
            for y in YEAR.findall(json.dumps(call.get("arguments", {}), ensure_ascii=False)):
                if int(y) < 2026 and y not in user_text:
                    hits.add("year_mismatch")
    if repeats >= 2:
        hits.add("same_result")
    thinks, flails = [], 0
    for row in rows:
        out = "".join(row["text"][a:b] for a, b in row["loss_spans"])
        m = THINK.search("<think" + out) or THINK.search(out)
        think = m.group(1) if m else ""
        if not m:
            hits.add("no_think")
        if len(think) > 900:
            hits.add("long_think")
        if thinks and think and difflib.SequenceMatcher(None, thinks[-1][:600], think[:600]).ratio() >= 0.9:
            hits.add("think_copy")
        thinks.append(think)
        if FLAIL.search(think):
            flails += 1
        if ENV.search(URL.sub(" ", out)):
            hits.add("env_aware")
        if forbidden_call(row):
            hits.add("forbidden_call")
    if flails >= 2:
        hits.add("flail")
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rows", nargs="+")
    ap.add_argument("--out")
    ap.add_argument("--ignore", default="", help="comma-separated reasons to report but not drop")
    args = ap.parse_args()
    ignore = set(filter(None, args.ignore.split(",")))
    out = open(args.out, "w") if args.out else None
    total = collections.Counter()
    for path in args.rows:
        turns = collections.defaultdict(list)
        source = None
        for line in open(path, encoding="utf-8"):
            row = json.loads(line)
            m = meta(row)
            source = source or m.get("source")
            turns[(m["case_id"], m["turn"])].append((m["step"], row))
        reasons = collections.Counter()
        cases = set()
        for (case, turn), steps in sorted(turns.items()):
            hits = scan_turn([r for _, r in sorted(steps, key=lambda x: x[0])])
            for h in hits:
                reasons[h] += 1
            if hits - ignore:
                cases.add(case)
            if hits and out:
                out.write("%s\t%s#%d\t%s\n" % (source, case, turn, ",".join(sorted(hits))))
        total.update(reasons)
        ncases = len({c for c, _ in turns})
        print("%-55s cases %4d drop %4d  %s" % (path[-55:], ncases, len(cases), dict(reasons)))
    print("total", dict(total))


if __name__ == "__main__":
    main()

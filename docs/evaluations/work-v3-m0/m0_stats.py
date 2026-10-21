#!/usr/bin/env python3
"""work-v3 M0: how much of the v2.1 pack and the 10-17 exam runs the new
tool rules touch (docs/design/agent-tool-v3.md §2.12).

  python3 docs/evaluations/work-v3-m0/m0_stats.py > docs/evaluations/work-v3-m0/stats.json
"""
import ast
import collections
import json
import re
import sys

PACK = "local/runs/distill/v21/final-20261018-ctx16k/train-rows.jsonl"
PACK8K = "local/runs/distill/v21/final-20261018/train-rows.jsonl"
EXAM = ["local/runs/exam-20261017/v21-lr2e-5-e2-think-full-k0",
        "local/runs/exam-20261017/v21-lr2e-5-e2-think-full-k1"]
WINDOW_LINES, WINDOW_BYTES = 200, 12 * 1024
RESP = re.compile(r"<tool_response>(.*?)</tool_response>", re.S)

# Errors work-v3 turns into successes (§2.3, §2.9, §2.10).
FIXED = {
    "replace_lines": [r"end_line \d+ beyond last line"],
    "calculator": [r"function \\?\"(sqrt|pow|ln|log10|log|exp)\\?\" is not allowed",
                   r"operator .{0,8} is not allowed"],
    "data_query": [r"requires exactly one of field or expression\"?\}?$",
                   r"count does not accept field or expression"],
}


def meta(row):
    m = row["meta"]
    return m if isinstance(m, dict) else ast.literal_eval(m)


def window_cut(content):
    lines = content.split("\n")
    if content.endswith("\n"):
        lines = lines[:-1]
    size = 0
    for index, line in enumerate(lines):
        size += len(line.encode()) + 1
        if index + 1 > WINDOW_LINES or size > WINDOW_BYTES:
            return True, len(lines), len(content.encode())
    return False, len(lines), len(content.encode())


def responses(text):
    for match in RESP.finditer(text):
        try:
            yield json.loads(match.group(1))
        except json.JSONDecodeError:
            continue


def pack_stats(path):
    hits = collections.defaultdict(set)
    trajectories = set()
    for line in open(path):
        row = json.loads(line)
        m = meta(row)
        key = "%s#%d" % (m["case_id"], m["turn"])
        trajectories.add(key)
        for resp in responses(row["text"]):
            tool = resp.get("tool")
            if tool == "read_file" and resp.get("ok"):
                cut, _, _ = window_cut(resp.get("result", {}).get("content", ""))
                if cut:
                    hits["read_file_window"].add(key)
            if tool == "read_lines":
                hits["read_lines_call"].add(key)
            if tool in FIXED and not resp.get("ok"):
                err = json.dumps(resp, ensure_ascii=False)
                if any(re.search(p, err) for p in FIXED[tool]):
                    hits[tool + "_now_succeeds"].add(key)
    return trajectories, hits


def exam_stats(run):
    sizes = []
    last = {}
    for line in open(run + "/trace.jsonl"):
        r = json.loads(line)
        if r["kind"] == "model_call":
            last[(r["case_id"], r["turn"])] = r["model_call"]["request"]["prompt"]
    seen = set()
    for (case, turn), prompt in last.items():
        for resp in responses(prompt):
            if resp.get("tool") != "read_file" or not resp.get("ok"):
                continue
            content = resp["result"]["content"]
            ident = (case, resp["result"]["path"], len(content))
            if ident in seen:
                continue
            seen.add(ident)
            cut, lines, size = window_cut(content)
            sizes.append({"case": case, "path": resp["result"]["path"], "lines": lines,
                          "bytes": size, "cut": cut, "truncated_64k": resp["result"].get("truncated", False)})
    return sizes


def main():
    out = {}
    for name, path in (("pack16k", PACK), ("pack8k", PACK8K)):
        trajectories, hits = pack_stats(path)
        union = set().union(*hits.values()) if hits else set()
        out[name] = {
            "path": path,
            "turn_trajectories": len(trajectories),
            "by_kind": {k: {"trajectories": len(v), "cases": len({x.split("--")[0].split("#")[0] for x in v}),
                            "ids": sorted(v)} for k, v in sorted(hits.items())},
            "needs_reteacher": len(union - hits.get("read_lines_call", set())),
            "needs_reteacher_ids": sorted(union - hits.get("read_lines_call", set())),
        }
    out["exam"] = {}
    for run in EXAM:
        reads = exam_stats(run)
        lines = sorted(x["lines"] for x in reads)
        sizes = sorted(x["bytes"] for x in reads)
        pick = lambda v, q: v[min(len(v) - 1, int(len(v) * q))]
        out["exam"][run.rsplit("/", 1)[1]] = {
            "distinct_reads": len(reads),
            "lines_p50_p90_p99_max": [pick(lines, .5), pick(lines, .9), pick(lines, .99), lines[-1]],
            "bytes_p50_p90_p99_max": [pick(sizes, .5), pick(sizes, .9), pick(sizes, .99), sizes[-1]],
            "cut_by_window": sum(x["cut"] for x in reads),
            "cut_by_200_lines_only": sum(x["lines"] > WINDOW_LINES for x in reads),
            "truncated_64k": sum(x["truncated_64k"] for x in reads),
            "cut_cases": sorted({x["case"] for x in reads if x["cut"]}),
        }
    json.dump(out, sys.stdout, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()

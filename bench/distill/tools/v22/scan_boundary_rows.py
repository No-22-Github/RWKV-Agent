#!/usr/bin/env python3
"""v2.2 plan §3: scan the agent-tool-v3.1 re-rendered v2.1 rows for the three boundary
patterns the 10-17 exam traced back to the training set.

  python3 bench/distill/tools/v22/scan_boundary_rows.py

1. empty_then_local: the last tool result before the supervised step came back
   empty (no search hits, no listing entries, file not found, empty web search)
   and the supervised step calls a local tool again.
2. calc_first: the first supervised step of a user turn calls calculator.
3. web_never_online: a web-scenario trajectory that never calls web_search or
   web_fetch.

Writes local/runs/distill/v21-v3/boundary.json with every hit and the user
prompt, for the per-trajectory decision in the v2.2 row-fix report.
"""
import ast
import collections
import glob
import json
import re

KEPT = "local/runs/distill/v21-v3/kept/*.jsonl"
OUT = "local/runs/distill/v21-v3/boundary.json"
LOCAL = {"search_text", "list_files", "read_file", "bash"}
RESP = re.compile(r"<tool_response>(.*?)</tool_response>", re.S)
CALL = re.compile(r'<tool_call>\{"name":"(\w+)"')
ONLINE_HINT = re.compile(r"网上|上网|联网|最新|官网|官方|新闻|online|latest|official|website|web", re.I)


def meta(row):
    m = row["meta"]
    return m if isinstance(m, dict) else ast.literal_eval(m)


def empty(resp):
    if not resp.get("ok", True):
        error = json.dumps(resp, ensure_ascii=False)
        return bool(re.search(r"ENOENT|no such file|not found|不存在", error))
    result = resp.get("result") or {}
    tool = resp.get("tool")
    if tool == "search_text":
        return not result.get("matches")
    if tool == "list_files":
        return not result.get("entries")
    if tool == "web_search":
        return not result.get("results")
    return False


def user_prompt(text):
    turns = [t for t in re.findall(r"\nUser: (?!<tool_response>)(.*?)(?=\n\nAssistant:)", text, re.S)
             if not t.startswith(("Use the Tool results", "Tool result"))]
    return turns[-1].strip()[:300] if turns else ""


def main():
    hits = collections.defaultdict(list)
    trajectories = collections.defaultdict(list)
    for path in sorted(glob.glob(KEPT)):
        source = path.rsplit("/", 1)[1][:-6]
        for line in open(path):
            row = json.loads(line)
            m = meta(row)
            key = "%s#%d" % (m["case_id"], m["turn"])
            supervised = "".join(row["text"][a:b] for a, b in row["loss_spans"])
            calls = CALL.findall(supervised)
            prompt_part = row["text"][: row["loss_spans"][0][0]]
            trajectories[(source, key)].append((m["step"], calls, prompt_part))
            responses = [json.loads(x) for x in RESP.findall(prompt_part) if x.startswith("{")]
            if responses and calls and calls[0] in LOCAL and empty(responses[-1]):
                prompt = user_prompt(row["text"])
                hits["empty_then_local"].append({
                    "source": source, "trajectory": key, "step": m["step"], "after": responses[-1].get("tool"),
                    "next": calls[0], "web_scenario": m["case_id"].startswith(("web-", "hyb-")),
                    "online_hint": bool(ONLINE_HINT.search(prompt)), "prompt": prompt})
            if m["step"] == 1 and calls[:1] == ["calculator"]:
                hits["calc_first"].append({"source": source, "trajectory": key, "prompt": user_prompt(row["text"])})
    for (source, key), steps in trajectories.items():
        if not key.startswith("web-"):
            continue
        used = {c for _, calls, _ in steps for c in calls}
        if not used & {"web_search", "web_fetch"}:
            steps.sort()
            hits["web_never_online"].append({"source": source, "trajectory": key, "first_calls": steps[0][1],
                                              "prompt": user_prompt(steps[-1][2] + "\n\nAssistant:")})
    # Decisions (v2.2-row-fixes report): drop web-type trajectories that kept
    # searching locally after an empty result, and no-tool (nt-) trajectories
    # that open with calculator. b22a / b22d supply the replacements.
    drop = sorted({(h["source"], h["trajectory"]) for h in hits["empty_then_local"]
                   if h["web_scenario"] or h["online_hint"]} |
                  {(h["source"], h["trajectory"]) for h in hits["calc_first"] if h["trajectory"].startswith("nt-")})
    with open(OUT.replace(".json", "-drop.txt"), "w") as out:
        out.write("".join("%s\t%s\n" % item for item in drop))
    summary = {k: len(v) for k, v in hits.items()}
    summary["drop"] = len(drop)
    summary["empty_then_local_web_or_hint"] = sum(1 for h in hits["empty_then_local"] if h["web_scenario"] or h["online_hint"])
    json.dump({"summary": summary, **hits}, open(OUT, "w"), ensure_ascii=False, indent=1)
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()

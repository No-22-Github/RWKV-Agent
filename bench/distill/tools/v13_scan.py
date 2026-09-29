#!/usr/bin/env python3
"""Scan the v1.2 training rows for trajectories that do not look like normal use.

  v13_scan.py [--v12 <mixed/rendered/all.jsonl>] [--out bench/distill/v13/scan-v12.json]

Each row is checked against the patterns below; the output lists the flagged
rows per pattern and the resulting fix lists that docs/distill/distill-allocation-v1.3.md §3
tells the executor to apply. Rows are keyed "<script entry>#<turn>".

  pattern                    fix
  bare_unknown               re-solve (case edited to answer_style natural first)
  markdown_final             re-solve: plain text, 1-4 sentences
  long_refusal  (> 400)      re-solve: 1-2 sentences, what / why / alternative
  long_smalltalk (> 800)     re-solve: short
  templated_clarify          re-solve: ask in your own words
  ls_despite_path_in_prompt  re-solve: open the named file directly
  repeated_identical_call    drop
  same_file_read_twice       drop
  verbose_under_answer_only  drop
  write_done_only            none: the prompt asks for DONE (contract, not a defect)

base700 rows cannot be re-rendered (they come from transformed records), so
every flagged base700 row is dropped instead of re-solved.
"""
import argparse
import json
import os
import re
from collections import Counter, defaultdict

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
V12 = os.path.join(REPO, "local", "outputs", "workspace-agent-distill-clean-20260928-v1.2",
                   "mixed", "rendered", "all.jsonl")
SUFFIX = "\n\nUser:"
CALL = re.compile(r"<tool_call>(\{.*\})</tool_call>", re.S)
RESOLVE = ["bare_unknown", "markdown_final", "long_refusal", "long_smalltalk",
           "templated_clarify", "ls_despite_path_in_prompt"]
DROP = ["repeated_identical_call", "same_file_read_twice", "verbose_under_answer_only"]


def outputs(row):
    return [row["text"][s:e].removesuffix(SUFFIX) for s, e in row["loss_spans"]]


def prompt_of(row):
    head = row["text"][: row["loss_spans"][0][0]]
    i = head.rfind("\n\nUser: ")
    return head[i + 8:] if i >= 0 else ""


def scan(row):
    m = row["meta"]
    outs = outputs(row)
    final, prompt = outs[-1], prompt_of(row)
    calls = []
    for o in outs[:-1]:
        match = CALL.search(o)
        if match:
            calls.append(json.loads(match.group(1)))
    names = [c["name"] for c in calls]
    sigs = [json.dumps(c, sort_keys=True) for c in calls]
    reads = [c["arguments"].get("path") for c in calls if c["name"] == "read_file" and c["arguments"].get("path")]
    found = []
    if final.strip() == "UNKNOWN":
        found.append("bare_unknown")
    if len(sigs) != len(set(sigs)):
        found.append("repeated_identical_call")
    if len(reads) != len(set(reads)):
        found.append("same_file_read_twice")
    if names[:1] == ["list_files"]:
        opened = [c["arguments"].get("path") for c in calls if c["name"] in ("read_file", "read_lines", "data_query")]
        if any(p and p in prompt for p in opened):
            found.append("ls_despite_path_in_prompt")
    if re.search(r"\*\*|^#+ |^\s*[-*] |```", final, re.M) and m["kind"] not in ("write", "script"):
        found.append("markdown_final")
    if m["kind"] == "refuse" and len(final) > 400:
        found.append("long_refusal")
    if m["kind"] == "smalltalk" and len(final) > 800:
        found.append("long_smalltalk")
    if (m["kind"] in ("direct", "local", "web", "web_local")
            and "Reply with only the final answer" in prompt and len(final) > 80):
        found.append("verbose_under_answer_only")
    if m["kind"] == "clarify" and re.search(r"lists two .*, .* and .*\. Which one do you mean\?", final):
        found.append("templated_clarify")
    if m["kind"] == "write" and final.strip() == "DONE":
        found.append("write_done_only")
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--v12", default=V12)
    ap.add_argument("--out", default=os.path.join(REPO, "bench", "distill", "v13", "scan-v12.json"))
    args = ap.parse_args()
    rows = [json.loads(line) for line in open(args.v12)]
    patterns = defaultdict(list)
    source = {}
    for row in rows:
        m = row["meta"]
        key = "%s#%d" % (m["case_id"], m["turn"])
        source[key] = m["source"]
        for name in scan(row):
            patterns[name].append(key)

    def entry(key):
        return key.split("#")[0]

    flagged = {k for name in RESOLVE + DROP for k in patterns[name]}
    resolve_keys = {k for name in RESOLVE for k in patterns[name] if source[k] != "base700"}
    drop_keys = {k for name in DROP for k in patterns[name] if source[k] != "base700"} - resolve_keys
    base700_drop = {k for k in flagged if source[k] == "base700"}
    result = {
        "input": os.path.relpath(args.v12, REPO),
        "rows": len(rows),
        "patterns": {name: sorted(keys) for name, keys in sorted(patterns.items())},
        "fix": {
            # Bank case IDs to re-solve with step.py (the new path replaces every old path of the case).
            "resolve_cases": sorted({entry(k).rsplit("--p", 1)[0] for k in resolve_keys}),
            # Script entries whose rows leave the set (append to bench/distill/exclude.jsonl).
            "drop_entries": sorted({entry(k) for k in drop_keys}),
            "base700_drop_entries": sorted({entry(k) for k in base700_drop}),
            # The TR-ABSENT cases whose prompt and expect change before re-solving (§3.2).
            "absent_cases": sorted({entry(k).rsplit("--p", 1)[0] for k in patterns["bare_unknown"]
                                    if source[k] != "base700"}),
        },
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("%-28s %5s  %s" % ("pattern", "rows", "by source"))
    for name, keys in sorted(patterns.items(), key=lambda kv: -len(kv[1])):
        print("%-28s %5d  %s" % (name, len(keys), dict(Counter(source[k] for k in keys))))
    print({k: len(v) for k, v in result["fix"].items()})


if __name__ == "__main__":
    main()

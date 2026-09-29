#!/usr/bin/env python3
"""N10 closeout-recovery paths: re-issue an earlier read right before the final answer.

  v13_closeout.py --script <scripts.jsonl> [--script ...] --out <closeout.jsonl> [--n 100]
                  [--cases bench/distill/cases]

The v1.2 bench's first cause of death was the closeout stage: a repeated call is
rejected, the harness switches to the answer stage, and the model emits yet
another <tool_call> (docs/distill/distill-allocation-v1.3.md §1.1). No v1.2 row
ever showed that stage. This takes passed single-turn paths and inserts a
verbatim copy of one earlier read immediately before the final answer, marked
supervised:false. `corpus render` then replays it through the real harness:
the copy is rejected as a duplicate, the harness writes its own rejection and
answer-stage prompts, and the unchanged final answer is scored and supervised.

No bytes are spliced here. The rejected copy is outside loss_spans, so a
mask-aware trainer never learns to repeat; a full-text trainer would, which is
why N10 must not ship to one.
"""
import argparse
import glob
import hashlib
import json
import os
import re

# Only local reads: web_search / web_fetch are replayable, so the harness
# re-executes a repeated web call instead of rejecting it and no closeout stage
# follows (6 of 100 in the 2026-09-30 smoke). data_query is left out until a
# render proves it is rejected too.
READS = {"list_files", "read_file", "read_lines", "search_text"}
WRITES = {"write_file", "replace_lines", "append_file"}
CALL = re.compile(r'^<tool_call>\{"name":"([a-z_]+)"')
SEPARATOR = "--p"
FIRST_PATH = 81


def tool_of(text):
    match = CALL.match(text)
    return match.group(1) if match else None


def eligible(entry):
    outs = entry["outputs"]
    tools = [tool_of(o["text"]) for o in outs]
    # Single turn: exactly one non-call output and it is the last one.
    if tools[-1] is not None or any(t is None for t in tools[:-1]):
        return None
    if not all(o["supervised"] for o in outs):
        return None
    calls = tools[:-1]
    if len(calls) < 2 or any(t in WRITES for t in calls):
        return None
    reads = [i for i, t in enumerate(calls) if t in READS]
    return reads or None


def load_cases(root):
    cases = {}
    for path in glob.glob(os.path.join(root, "*", "*", "case.json")):
        case = json.load(open(path))
        cases[case["id"]] = case
    return cases


def digest(text):
    return int(hashlib.sha256(text.encode()).hexdigest(), 16)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", action="append", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--cases", default="bench/distill/cases")
    args = ap.parse_args()
    cases = load_cases(args.cases)
    # Batch scripts share entry IDs (cfg-5006--p1 is in b01 and b02): first wins.
    entries = {}
    for path in args.script:
        for line in open(path):
            entry = json.loads(line)
            entries.setdefault(entry["case_id"], entry)
    entries = list(entries.values())
    by_case, picked = set(), []
    for entry in sorted(entries, key=lambda e: digest(e["case_id"])):
        base = entry["case_id"][: entry["case_id"].rfind(SEPARATOR)]
        reads = eligible(entry)
        case = cases.get(base)
        if reads is None or base in by_case or case is None or len(case["turns"]) != 1:
            continue
        # A rejected copy still counts against expect.max_calls.
        if (case.get("expect") or {}).get("max_calls"):
            continue
        by_case.add(base)
        source = reads[digest(entry["case_id"] + "#dup") % len(reads)]
        outs = entry["outputs"]
        copy = {"text": outs[source]["text"], "supervised": False}
        picked.append(({
            "case_id": "%s%s%d" % (base, SEPARATOR, FIRST_PATH),
            "outputs": outs[:-1] + [copy, outs[-1]],
        }, entry["case_id"], source + 1))
        if len(picked) == args.n:
            break
    # The replay loader rejects unknown keys, so provenance goes to a sidecar.
    with open(args.out, "w") as f, open(args.out + ".provenance.tsv", "w") as side:
        side.write("entry\tfrom\tduplicated_output\n")
        for rec, origin, position in picked:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            side.write("%s\t%s\t%d\n" % (rec["case_id"], origin, position))
    print("eligible cases used: %d (asked %d)" % (len(picked), args.n))


if __name__ == "__main__":
    main()

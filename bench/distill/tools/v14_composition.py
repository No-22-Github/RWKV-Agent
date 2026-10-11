#!/usr/bin/env python3
"""v1.4 §5 composition table over the whole v1.4 row set (read-only).

  python3 bench/distill/tools/v14_composition.py [--json out.json]

Rows: v1.3 kept train+val rows, b09, b10-pilot, b10a–b10e and b11 renders, minus
every row common/exclude.jsonl strikes (an entry only strikes rows of its own
batch; an entry without a batch strikes every batch — same rule as
v14_m1_closeout.py). Language = CJK in the case prompt of the row's turn.
"""
import argparse
import collections
import json
import os
import re

from distill_paths import EXCLUDE_JSONL, REPO, case_files

R = os.path.join(REPO, "local", "runs", "distill")
SOURCES = [os.path.join(R, "v13-clean", "train-rows.jsonl"), os.path.join(R, "v13-clean", "val-rows.jsonl"),
           os.path.join(R, "v14", "b09", "rows.jsonl")] + \
          [os.path.join(R, "v141", b, "corpus", "rows.jsonl") for b in ("b10-pilot", "b10a", "b10b", "b10c", "b10d", "b10e", "b11")]
NEW = {"b10-pilot", "b10a", "b10b", "b10c", "b10d", "b10e"}
CJK = re.compile(r"[一-鿿]")
PATH = re.compile(r"[\w一-鿿.-]+/[\w一-鿿./-]*\.\w+|\b[\w-]+\.(?:csv|ya?ml|json|toml|ini|env|md|txt|log|py|conf)\b")
TOOLS = re.compile(r"<tools>\[(.*?)\]</tools>", re.S)


def batch_of(meta):
    return meta.get("source", "").removeprefix("distill-")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    args = ap.parse_args()
    ex = collections.defaultdict(set)
    for line in open(EXCLUDE_JSONL):
        if line.strip():
            e = json.loads(line)
            ex[e["case_id"]].add(e.get("batch", ""))
    prompts = {}
    for p in case_files():
        c = json.load(open(p))
        prompts[c["id"]] = [t["prompt"] for t in c["turns"]]
    rows = []
    for path in SOURCES:
        for line in open(path):
            r = json.loads(line)
            m = r["meta"]
            b = ex.get(m["case_id"])
            if b and ("" in b or batch_of(m) in b):
                continue
            rows.append(r)
    N = len(rows)
    by_batch = collections.Counter(batch_of(r["meta"]) for r in rows)
    pct = lambda a, b: "%d/%d (%.1f%%)" % (a, b, 100.0 * a / b) if b else "0/0"

    def prompt(r):
        m = r["meta"]
        ps = prompts.get(m["case_id"].rsplit("--p", 1)[0])
        if ps and m["turn"] <= len(ps):
            return ps[m["turn"] - 1]
        # base700 records have no live case.json. The first supervised output
        # follows the current real user prompt, before any current-turn receipt.
        head = r["text"][:r["loss_spans"][0][0]]
        if "\n\nUser: " not in head:
            raise ValueError("no user prompt for %s" % m["case_id"])
        return head.rsplit("\n\nUser: ", 1)[1].rsplit("\n\nAssistant: ", 1)[0]

    def final(r):
        a, b = r["loss_spans"][-1]
        return r["text"][a:b].removesuffix("\n\nUser:").strip()

    zh = [bool(CJK.search(prompt(r))) for r in rows]
    val = [r["meta"]["traj"]["final_kind"] == "value" for r in rows]
    calls = collections.Counter(t for r in rows for t in r["meta"]["traj"]["tool_seq"])
    ntools = []
    for r in rows:
        m = TOOLS.search(r["text"])
        ntools.append(m.group(1).count('{"name":') if m else 0)
    writes = [r["meta"]["traj"].get("writes") or prompt(r) and r["meta"]["case_tags"].get("scenario") == "script" for r in rows]
    t1 = [r for r in rows if r["meta"]["turn"] == 1]
    t1_tool = [r for r in t1 if r["meta"]["traj"]["tool_seq"]]
    first_lf = [r for r in t1_tool if r["meta"]["traj"]["tool_seq"][0] == "list_files"]
    with_path = [r for r in t1_tool if PATH.search(prompt(r))]
    with_path_lf = [r for r in with_path if r["meta"]["traj"]["tool_seq"][0] == "list_files"]
    new_w = [r for r in rows if batch_of(r["meta"]) in NEW and r["meta"]["traj"].get("writes")]
    W = {"write_file", "replace_lines", "append_file"}
    rb = 0
    for r in new_w:
        seq = r["meta"]["traj"]["tool_seq"]
        last = max(i for i, t in enumerate(seq) if t in W)
        rb += any(t in ("read_file", "read_lines") for t in seq[last + 1:])
    closeout = [r for r in rows if "duplicate tool call rejected" in r["text"] and "tools are now unavailable" in r["text"]]
    closeout_w = [r for r in closeout if r["meta"]["traj"].get("writes")]
    toks = [r["meta"]["traj"]["tokens"] for r in rows]
    out = collections.OrderedDict([
        ("rows", N), ("rows_by_batch", dict(sorted(by_batch.items()))),
        ("pure_value_finals", pct(sum(val), N)),
        ("pure_value_zh", pct(sum(v for v, z in zip(val, zh) if z), sum(zh))),
        ("pure_value_en", pct(sum(v for v, z in zip(val, zh) if not z), N - sum(zh))),
        ("bare_UNKNOWN_finals", sum(final(r) == "UNKNOWN" for r in rows)),
        ("UNKNOWN_contract_rows", pct(sum("UNKNOWN" in prompt(r) for r in rows), N)),
        ("zh_rows", pct(sum(zh), N)),
        ("multi_turn_rows", pct(sum(r["meta"]["traj"]["turns_total"] >= 2 for r in rows), N)),
        ("catalog_le5_rows", pct(sum(0 < n <= 5 for n in ntools), N)),
        ("data_query_share_of_calls", pct(calls["data_query"], sum(calls.values()))),
        ("write_or_script_rows", pct(sum(bool(w) for w in writes), N)),
        ("readback_after_last_write_new_rows", pct(rb, len(new_w))),
        ("closeout_rows", len(closeout)), ("closeout_write_rows", len(closeout_w)),
        ("zero_call_rows", pct(sum(r["meta"]["traj"]["zero_call"] for r in rows), N)),  # clean-v13 口径（全部行）
        ("zero_call_turn1", pct(sum(r["meta"]["traj"]["zero_call"] for r in t1), len(t1))),
        ("first_action_list_files", pct(len(first_lf), len(t1_tool))),
        ("first_action_list_files_when_prompt_names_path", pct(len(with_path_lf), len(with_path))),
        ("tokens_max", max(toks)), ("tokens_over_4096", pct(sum(t > 4096 for t in toks), N)),
    ])
    print(json.dumps(out, ensure_ascii=False, indent=1))
    if args.json:
        json.dump(out, open(args.json, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()

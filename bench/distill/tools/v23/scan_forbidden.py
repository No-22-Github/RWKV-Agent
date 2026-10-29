#!/usr/bin/env python3
"""List rendered rows that train a tool call after the harness disabled tools.

    python3 bench/distill/tools/v21/scan_forbidden.py ROWS.jsonl [...]

A row's prompt whose last User block says the tools are gone (answer stage,
rescue) while the trained output is a <tool_call> teaches exactly the
closeout failure v2.1 is meant to fix. Prints counts and the case ids;
finalize.py drops every row of such a case's turn.
"""
import json
import sys

GONE = ("tools are now unavailable", "tool calls are forbidden", "have been disabled",
        "The tools have been disabled")


def bad(row):
    a, _ = row["loss_spans"][-1]
    prompt = row["text"][:a]
    last_user = prompt.rsplit("\n\nAssistant:", 1)[0].rsplit("\n\nUser: <tool_response>", 1)[-1]
    out = row["text"][a:]
    return any(g in last_user for g in GONE) and "<tool_call>" in out


if __name__ == "__main__":
    for path in sys.argv[1:]:
        rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
        hits = sorted({(r["meta"]["case_id"], r["meta"]["turn"]) for r in rows if bad(r)})
        print(path, len(rows), "rows;", len(hits), "turns with a tool call after tools were disabled:", hits[:10])

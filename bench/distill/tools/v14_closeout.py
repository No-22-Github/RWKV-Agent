#!/usr/bin/env python3
"""b11 N10 closeout-recovery paths for v1.4 (§3.10): v13_closeout.py's transform on
the v1.4 teacher scripts, now covering write and script tasks too.

  v14_closeout.py --script b09=<b09-m1.jsonl> --script b10a=<b10a.jsonl> ... \
                  --out <b11.jsonl> [--n 200] [--min-write 60]

Each picked path gets a verbatim copy of one earlier local read inserted right
before the final answer, supervised:false. `corpus render` replays it: the copy
is rejected as a duplicate, the harness enters the answer stage, and the
unchanged final answer is scored and supervised (the rejected copy stays
outside loss_spans). Differences from v13_closeout.py:

- sources are the v1.4 batch scripts; paths struck in common/exclude.jsonl for
  their batch are skipped; new path ids use --p91 (b09's rewrite owns --p90);
- write / script paths are eligible: the copied read must come after the last
  write (the read-back), so the duplicate re-reads the edited file; at least
  --min-write of the --n rows are write/script paths.
"""
import argparse
import hashlib
import json
import re

from distill_paths import EXCLUDE_JSONL, case_files

READS = {"list_files", "read_file", "read_lines", "search_text"}
WRITES = {"write_file", "replace_lines", "append_file"}
CALL = re.compile(r'^<tool_call>\{"name":"([a-z_]+)"')
SEPARATOR = "--p"
FIRST_PATH = 91


def tool_of(text):
    match = CALL.match(text)
    return match.group(1) if match else None


def eligible(entry):
    """-> (kind, candidate read indices) or None. kind is 'write' or 'read'."""
    outs = entry["outputs"]
    tools = [tool_of(o["text"]) for o in outs]
    if tools[-1] is not None or any(t is None for t in tools[:-1]):
        return None  # single turn only: one final answer, last
    if not all(o["supervised"] for o in outs):
        return None
    calls = tools[:-1]
    if len(calls) < 2:
        return None
    writes = [i for i, t in enumerate(calls) if t in WRITES]
    if writes:
        reads = [i for i, t in enumerate(calls) if t in READS and i > writes[-1]]
        return ("write", reads) if reads else None
    reads = [i for i, t in enumerate(calls) if t in READS]
    return ("read", reads) if reads else None


def digest(text):
    return int(hashlib.sha256(text.encode()).hexdigest(), 16)


def capped(case):
    """A rejected copy still counts against max_calls, so skip capped cases."""
    if (case.get("expect") or {}).get("max_calls"):
        return True
    return any((t.get("expect") or {}).get("max_calls") for t in case["turns"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", action="append", required=True, help="batch=path")
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--min-write", type=int, default=60)
    args = ap.parse_args()
    cases = {}
    for path in case_files():
        case = json.load(open(path))
        cases[case["id"]] = case
    struck = set()
    for line in open(EXCLUDE_JSONL):
        if line.strip():
            e = json.loads(line)
            struck.add((e.get("batch", ""), e["case_id"]))
    pools = {"write": [], "read": []}
    seen = set()
    for spec in args.script:
        batch, path = spec.split("=", 1)
        for line in open(path):
            entry = json.loads(line)
            if (batch, entry["case_id"]) in struck:
                continue
            base = entry["case_id"][: entry["case_id"].rfind(SEPARATOR)]
            case = cases.get(base)
            got = eligible(entry)
            if got is None or case is None or len(case["turns"]) != 1 or capped(case):
                continue
            pools[got[0]].append((digest(entry["case_id"]), base, batch, entry, got[1]))
    picked = []
    for kind, quota in (("write", args.min_write), ("read", args.n)):
        for _, base, batch, entry, reads in sorted(pools[kind]):
            if len(picked) >= args.n or (kind == "write" and quota <= 0):
                break
            if base in seen:
                continue
            seen.add(base)
            quota -= 1
            source = reads[digest(entry["case_id"] + "#dup") % len(reads)]
            outs = entry["outputs"]
            copy = {"text": outs[source]["text"], "supervised": False}
            picked.append(({"case_id": "%s%s%d" % (base, SEPARATOR, FIRST_PATH),
                            "outputs": outs[:-1] + [copy, outs[-1]]},
                           batch, entry["case_id"], source + 1, kind))
    # The replay loader rejects unknown keys, so provenance goes to a sidecar.
    with open(args.out, "w") as f, open(args.out + ".provenance.tsv", "w") as side:
        side.write("entry\tbatch\tfrom\tduplicated_output\tkind\n")
        for rec, batch, origin, position, kind in picked:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            side.write("%s\t%s\t%s\t%d\t%s\n" % (rec["case_id"], batch, origin, position, kind))
    kinds = [p[4] for p in picked]
    print("picked %d (write/script %d, read %d); eligible write %d, read %d"
          % (len(picked), kinds.count("write"), kinds.count("read"), len(pools["write"]), len(pools["read"])))


if __name__ == "__main__":
    main()

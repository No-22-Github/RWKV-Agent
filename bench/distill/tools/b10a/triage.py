#!/usr/bin/env python3
"""pass@3 triage over three agent-eval teacher runs (v1.4 b10a S5).

  python3 triage.py --run dir --run dir --run dir [--zeros]

Prints the pass@3 distribution and, with --zeros, per-case failure reasons of
the 0/3 cases (final answer of each run + scorer failures).
"""
import argparse
import collections
import json
import os


def load(run):
    s = json.load(open(os.path.join(run, "summary.json")))
    out = {}
    for c in s["cases"]:
        turns = []
        for t in c["turns"]:
            turns.append({"prompt": (t.get("prompt") or "")[:100],
                          "output": (t.get("result") or {}).get("output") or "",
                          "failures": t.get("failures") or [],
                          "steps": len((t.get("result") or {}).get("steps") or []),
                          "tool_calls": t.get("tool_calls", c.get("tool_calls", 0))})
        out[c["id"]] = {"passed": bool(c.get("passed")), "turns": turns}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="append", required=True)
    ap.add_argument("--zeros", action="store_true")
    args = ap.parse_args()
    runs = [load(r) for r in args.run]
    ids = sorted(set().union(*[set(r) for r in runs]))
    dist = collections.Counter()
    zeros = []
    for cid in ids:
        n = sum(1 for r in runs if r.get(cid, {}).get("passed"))
        dist[n] += 1
        if n == 0:
            zeros.append(cid)
    print("pass@3 over %d cases: 3/3=%d  2/3=%d  1/3=%d  0/3=%d" % (
        len(ids), dist[3], dist[2], dist[1], dist[0]))
    if args.zeros:
        for cid in zeros:
            print("\n== %s" % cid)
            for i, r in enumerate(runs):
                if cid not in r:
                    print("  k%d: <missing>" % i)
                    continue
                for t in r[cid]["turns"]:
                    print("  k%d steps=%d tools=%s fail=%s" % (i, t["steps"], t["tool_calls"],
                                                               "; ".join(t["failures"])[:180] or "-"))
                    print("     final: %s" % t["output"].replace("\n", " ⏎ ")[:220])


if __name__ == "__main__":
    main()

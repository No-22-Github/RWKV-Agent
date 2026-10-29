#!/usr/bin/env python3
"""v2.3 plan §4.1: which stock trajectories survive the agent-tool-v3.2 replay.

A trajectory (case#turn) is kept when every row the v2.2 pack read for it
replays under agent-tool-v3.2 with byte-identical supervised spans and still
passes. Baselines: the v2.1/v2.0 rows the agent-tool-v3.0 replay kept
(local/runs/distill/v21-v3/kept/<name>.jsonl) and the v2.2 batch rows
(local/runs/distill/v22/<batch>/corpus/rows.jsonl). Run after rerender_v32.sh:

  python3 bench/distill/tools/v23/compare_v32.py

Writes local/runs/distill/v2.3/stock/kept/<name>.jsonl and compare.json.
"""
import ast
import collections
import json
import os

A = "local/runs/distill/v21-v3/kept"
B = "local/runs/distill/v22"
O = "local/runs/distill/v2.3/stock"
V21 = ["main", "b21i", "b21j", "b21k", "b21l", "b21m", "b21n", "b21o", "b21p", "ref-v20", "ref-v21",
       "ref-b21i", "ref-b21l", "ref-b21n", "v20app-qwen", "v20app-qwen-calc", "v20rec"]
V22 = ["b22a", "b22b", "b22c", "b22c-q38", "b22d", "b22e", "v21-redo", "v20-redo", "ref-v21-redo", "ref-v20-redo"]


def meta(row):
    m = row["meta"]
    return m if isinstance(m, dict) else ast.literal_eval(m)


def load(path):
    rows = {}
    for line in open(path, encoding="utf-8"):
        row = json.loads(line)
        m = meta(row)
        rows[(m["case_id"], m["turn"], m["step"])] = row
    return rows


def supervised(row):
    return [row["text"][a:b] for a, b in row["loss_spans"]]


def main():
    report = {}
    os.makedirs(f"{O}/kept", exist_ok=True)
    for name in V21 + V22:
        old = load(f"{A}/{name}.jsonl" if name in V21 else f"{B}/{name}/corpus/rows.jsonl")
        new_path = f"{O}/{name}/corpus/rows.jsonl"
        new = load(new_path) if os.path.exists(new_path) else {}
        reasons = collections.defaultdict(set)
        for key, row in old.items():
            traj = "%s#%d" % (key[0], key[1])
            other = new.get(key)
            if other is None:
                reasons[traj].add("not_replayed")
            elif supervised(other) != supervised(row):
                reasons[traj].add("supervised_changed")
            elif not meta(other).get("passed", False):
                reasons[traj].add("fails_now")
        kept = [new[k] for k in sorted(old) if "%s#%d" % (k[0], k[1]) not in reasons]
        with open(f"{O}/kept/{name}.jsonl", "w", encoding="utf-8") as out:
            for row in kept:
                out.write(json.dumps(row, ensure_ascii=False) + "\n")
        why = collections.Counter(r for rs in reasons.values() for r in rs)
        report[name] = {"old_rows": len(old), "kept_rows": len(kept),
                        "trajectories": len({"%s#%d" % (k[0], k[1]) for k in old}),
                        "dropped_trajectories": len(reasons), "why": dict(why),
                        "dropped": sorted(reasons)}
        print("%-17s rows %5d -> %5d  dropped %3d %s" % (name, len(old), len(kept), len(reasons), dict(why)))
    json.dump(report, open(f"{O}/compare.json", "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()

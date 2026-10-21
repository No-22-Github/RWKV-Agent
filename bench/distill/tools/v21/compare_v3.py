#!/usr/bin/env python3
"""agent-tool-v3.1 M5: which v2.1 training rows survive the agent-tool-v3.1 replay.

A row is kept when its trajectory (case#turn) replays under agent-tool-v3.1 with every
supervised span byte-identical, still passes, and is not on M0's list of
trajectories the new tool results no longer support (read past one screen,
replace_lines/calculator/data_query errors that now succeed). Everything else
goes to the re-teacher list. Run after rerender_v3.sh:

  python3 bench/distill/tools/v21/compare_v3.py
"""
import ast
import collections
import glob
import json
import os

V = "local/runs/distill/v21"
O = "local/runs/distill/v21-v3"
M0 = "docs/evaluations/work-v3-m0/stats.json"
# input name -> the rows file the 10-18 pack read (final-stats.json inputs)
INPUTS = {name: f"{V}/{name}/corpus/rows.jsonl" for name in
          ["main", "b21i", "b21j", "b21k", "b21l", "b21m", "b21n", "b21o", "b21p",
           "ref-v20", "ref-v21", "ref-b21i", "ref-b21l", "ref-b21n"]}
INPUTS["v20app-qwen"] = f"{V}/v20app-qwen/rows.jsonl"
INPUTS["v20app-qwen-calc"] = f"{V}/v20app-qwen-calc/rows.jsonl"
INPUTS["v20rec"] = f"{V}/v20rec/rows-dedup.jsonl"


def meta(row):
    m = row["meta"]
    return m if isinstance(m, dict) else ast.literal_eval(m)


def load(path):
    rows = {}
    for line in open(path):
        row = json.loads(line)
        m = meta(row)
        rows[(m["case_id"], m["turn"], m["step"])] = row
    return rows


def supervised(row):
    # rerender_v3.sh renames read_lines to read_file in the teacher's outputs;
    # that rename alone is not a change.
    return [row["text"][a:b].replace("read_lines", "read_file") for a, b in row["loss_spans"]]


def main():
    m0 = set(json.load(open(M0))["pack16k"]["needs_reteacher_ids"])
    report = {"inputs": {}, "reteacher": {}}
    os.makedirs(f"{O}/kept", exist_ok=True)
    totals = collections.Counter()
    for name, path in INPUTS.items():
        old = load(path)
        new_path = f"{O}/{name}/corpus/rows.jsonl"
        new = load(new_path) if os.path.exists(new_path) else {}
        reasons = collections.defaultdict(set)
        for key, row in old.items():
            traj = "%s#%d" % (key[0], key[1])
            if traj in m0:
                reasons[traj].add("m0")
            other = new.get(key)
            if other is None:
                reasons[traj].add("not_replayed")
            elif supervised(other) != supervised(row):
                reasons[traj].add("supervised_changed")
            elif not meta(other).get("passed", False):
                reasons[traj].add("fails_now")
        kept = [new[key] for key in sorted(old)
                if "%s#%d" % (key[0], key[1]) not in reasons]
        with open(f"{O}/kept/{name}.jsonl", "w") as out:
            for row in kept:
                out.write(json.dumps(row, ensure_ascii=False) + "\n")
        trajectories = {"%s#%d" % (k[0], k[1]) for k in old}
        why = collections.Counter(r for rs in reasons.values() for r in rs)
        report["inputs"][name] = {
            "old_rows": len(old), "kept_rows": len(kept),
            "trajectories": len(trajectories), "reteacher_trajectories": len(reasons),
            "reasons": dict(why),
        }
        report["reteacher"][name] = {t: sorted(r) for t, r in sorted(reasons.items())}
        totals.update(old_rows=len(old), kept_rows=len(kept), trajectories=len(trajectories),
                      reteacher=len(reasons))
    report["totals"] = dict(totals)
    # Re-teacher id lists, one per case tree, for
    # CASES=<tree> bench/distill/tools/v22/run_teacher.sh <batch> '*' 1 <list>
    trees = {"v2.1": "bench/distill/v2.1/cases", "v2.0": "bench/distill/v2.0/cases"}
    present = {tree: {os.path.basename(os.path.dirname(p)) for p in glob.glob(root + "/*/*/case.json")}
               for tree, root in trees.items()}
    os.makedirs(f"{O}/reteacher-ids", exist_ok=True)
    lists = collections.defaultdict(set)
    missing = set()
    for name, trajectories in report["reteacher"].items():
        tree = "v2.0" if name.startswith(("v20", "ref-v20")) else "v2.1"
        for traj in trajectories:
            base = traj.split("#")[0].split("--")[0]
            (lists[tree] if base in present[tree] else missing).add(base)
    for tree, ids in lists.items():
        with open(f"{O}/reteacher-ids/{tree}.txt", "w") as out:
            out.write("".join(i + "\n" for i in sorted(ids)))
    report["reteacher_cases"] = {tree: len(ids) for tree, ids in lists.items()}
    report["reteacher_cases_missing"] = sorted(missing)
    json.dump(report, open(f"{O}/compare.json", "w"), ensure_ascii=False, indent=1)
    for name, item in report["inputs"].items():
        print(f"{name:18s} rows {item['old_rows']:5d} -> {item['kept_rows']:5d}  "
              f"reteacher {item['reteacher_trajectories']:4d}/{item['trajectories']:4d}  {item['reasons']}")
    print("total", dict(totals))
    print("re-teacher cases", report["reteacher_cases"], "missing from case trees:", len(report["reteacher_cases_missing"]))


if __name__ == "__main__":
    main()

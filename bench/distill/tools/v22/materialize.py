#!/usr/bin/env python3
"""The v2.2 tool-set generator (work-v3): copies cases into a run directory
with a concrete, shuffled tool directory drawn from each case's tool_policy.
Same rule as v2.1's materialize.py over the 13-tool work-v3 catalog; a
tool_policy naming read_lines (cases written for work-v2) means read_file.

    python3 bench/distill/tools/v22/materialize.py --cases bench/distill/v2.2/cases \
        --out local/runs/distill/v22/<batch>/cases [--ids-glob 'hyb-34*'] [--salt v2.2-toolset]

The teacher runs on these copies and the corpus render replays the same
copies, so teacher and student face the same directory bytes (the harness
keeps the listed order because offered_tools_ordered is true). The draw is a
pure function of (salt, case id): re-running writes identical files.

Per case, with C = work-v3 (13 tools), M = must_offer, N = never_offer and
O = C - M - N the optional tools:
  45%  full       M + all of O
  35%  trimmed    M + O minus 1-4 random tools
  20%  tight      M + 1-3 random tools of O (2-4 when M is empty)
then the whole list is shuffled. A manifest.jsonl beside the cases records
each draw (mode, size, order).
"""
import argparse
import fnmatch
import glob
import hashlib
import json
import os
import random
import shutil

WORK_V3 = ["list_files", "read_file", "search_text", "write_file", "replace_lines",
           "append_file", "calculator", "data_query", "datetime", "web_search", "web_fetch",
           "bash", "get_weather"]


def v3_names(names):
    out = []
    for name in names:
        name = "read_file" if name == "read_lines" else name
        if name not in out:
            out.append(name)
    return out


def draw(case_id, policy, salt):
    rng = random.Random(int(hashlib.sha256((salt + ":" + case_id).encode()).hexdigest()[:16], 16))
    must = [t for t in WORK_V3 if t in set(v3_names(policy.get("must_offer", [])))]
    never = set(v3_names(policy.get("never_offer", [])))
    optional = [t for t in WORK_V3 if t not in must and t not in never]
    roll = rng.random()
    if roll < 0.45 or not optional:
        mode, keep = "full", list(optional)
    elif roll < 0.80:
        mode = "trimmed"
        drop = set(rng.sample(optional, min(len(optional) - 1, rng.randint(1, 4)))) if len(optional) > 1 else set()
        keep = [t for t in optional if t not in drop]
    else:
        mode = "tight"
        low, high = (1, 3) if must else (2, 4)
        keep = rng.sample(optional, min(len(optional), rng.randint(low, high)))
    offered = must + keep
    rng.shuffle(offered)
    return mode, offered


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--cases", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ids-glob", default="*")
    ap.add_argument("--ids-file", help="optional file with one case id per line")
    ap.add_argument("--salt", default="v2.2-toolset")
    args = ap.parse_args()
    wanted = None
    if args.ids_file:
        wanted = {line.strip() for line in open(args.ids_file) if line.strip()}
    if os.path.exists(args.out):
        raise SystemExit("--out %s already exists" % args.out)
    manifest = []
    for path in sorted(glob.glob(os.path.join(args.cases, "*", "*", "case.json"))):
        src = os.path.dirname(path)
        cid = os.path.basename(src)
        if not fnmatch.fnmatch(cid, args.ids_glob) or (wanted is not None and cid not in wanted):
            continue
        case = json.load(open(path, encoding="utf-8"))
        if "offered_tools" in case:
            raise SystemExit("%s already has offered_tools; v2.0 cases declare tool_policy only" % cid)
        mode, offered = draw(cid, case.get("tool_policy") or {}, args.salt)
        dst = os.path.join(args.out, os.path.basename(os.path.dirname(src)), cid)
        shutil.copytree(src, dst)
        rebuilt = {}
        for key, value in case.items():
            if key == "tool_policy":
                # The loader checks must_offer against offered_tools, so the
                # written policy has to use work-v3 names too. A v2.0 policy
                # that needs read_file but bans read_lines (whole-file reads
                # only) maps both to read_file; must_offer wins.
                value = {k: v3_names(v) if k in ("must_offer", "never_offer") else v
                         for k, v in value.items()}
                if "never_offer" in value:
                    must_names = set(value.get("must_offer", []))
                    value["never_offer"] = [t for t in value["never_offer"] if t not in must_names]
            rebuilt[key] = value
            if key == "turns":
                rebuilt["offered_tools"] = offered
                rebuilt["offered_tools_ordered"] = True
        with open(os.path.join(dst, "case.json"), "w", encoding="utf-8") as f:
            json.dump(rebuilt, f, ensure_ascii=False, indent=2)
            f.write("\n")
        manifest.append({"id": cid, "mode": mode, "n": len(offered), "offered_tools": offered})
    with open(os.path.join(args.out, "..", "toolsets.jsonl"), "w", encoding="utf-8") as f:
        for item in manifest:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    modes = {}
    for item in manifest:
        modes[item["mode"]] = modes.get(item["mode"], 0) + 1
    sizes = sorted(item["n"] for item in manifest)
    print("materialized %d case(s): %s; directory size min/median/max %d/%d/%d" % (
        len(manifest), modes, sizes[0], sizes[len(sizes) // 2], sizes[-1]) if manifest else "no cases")


if __name__ == "__main__":
    main()

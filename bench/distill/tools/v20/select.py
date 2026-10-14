#!/usr/bin/env python3
"""Picks the v2.0 (b20s) cases out of the 1.x distill banks and copies them
into bench/distill/v2.0/cases with a tool_policy.

    python3 bench/distill/tools/v20/select.py [--n 600] [--report PATH]

Pool: every case that has a passing teacher path in the v1.41 training pack
(local/runs/distill/v141/final-20261013/{train,validation}-rows.jsonl), minus
cases seeded from a test bank (base700). Per case it reads, from the pack rows:
the tools any kept path used, the final answers (length, Markdown), zero-call
first turn, multi-turn. The case itself comes from bench/distill/v*/cases.

Filters (v2.0 runs the teacher without the 1.x suffix, so cases whose 1.x
answers were already long or Markdown are the ones most likely to come back
unusable): every kept final answer <= 400 chars and Markdown-free. Cases whose
verify.py asserts the authored offered_tools are skipped (v2.0 draws the
directory per run). A re-run first deletes the previous b20s copies.
max_output_chars is removed from a turn whose prompt carries no length cue:
it was a hidden limit the 1.x suffix satisfied, and filter.py now caps every
agent final answer at 600 chars.

Quotas (deterministic, seed 20261014, one case per family):
  bash / get_weather (v1.41 b12)   90
  multi-turn                       120   (outside b12)
  zero-call first turn             120   (outside b12, single-turn)
  the rest by scenario, capped so no scenario exceeds 1.5x its fair share.

Copies are renamed <prefix>-2<4-digit id> (cfg-5003 -> cfg-25003) so they do
not collide with the 1.x originals when the loader reads bench/distill
recursively; tags.derived_from keeps the original id. tool_policy:
  must_offer  = tools a kept 1.x path used + required_tools + forbidden_tools
                (a trap has to be offered to be a trap)
  never_offer = for a case that authored offered_tools (v1.3 §2.12), the
                work-v1 tools it left out — the narrowed directory was the lesson.
Re-running rewrites the same files byte for byte.
"""
import argparse
import collections
import glob
import json
import os
import random
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from distill_paths import REPO, DISTILL, cases_dir  # noqa: E402

PACK = os.path.join(REPO, "local/runs/distill/v141/final-20261013")
WORK_V1 = ["list_files", "read_file", "search_text", "read_lines", "write_file", "replace_lines",
           "append_file", "calculator", "data_query", "datetime", "web_search", "web_fetch"]
WORK_V2 = WORK_V1 + ["bash", "get_weather"]
SEED = 20261014
CJK = re.compile(r"[一-鿿]")
MD = re.compile(r"^\s*#|\*\*|^\s*\|.*\|\s*$|^\s*[-*] |```", re.M)
LENGTH_CUE = re.compile(r"\d+\s*(个)?(字|characters?|chars|words)|一句|两句|三句|简短|简要|简洁|不超过|以内|brief|concise|"
                        r"one sentence|two sentences|only the|just the|只回答|只给|只输出|只说|只要|仅回答", re.I)
SCENARIO_PREFIX = {"tabular": "tab", "logs": "log", "config": "cfg", "docs": "doc", "filesystem": "fs",
                   "script": "scr", "code": "code", "web": "web", "hybrid": "hyb", "notool": "nt"}


def tool_name(text):
    m = re.match(r'\s*<tool_call>\s*\{"name"\s*:\s*"([a-z_]+)"', text)
    return m.group(1) if m else None


def load_pool():
    info = {}
    for split in ("train", "validation"):
        for line in open(os.path.join(PACK, split + "-rows.jsonl"), encoding="utf-8"):
            row = json.loads(line)
            meta = row["meta"]
            base = re.sub(r"--p\d+$", "", meta["case_id"])
            a, b = row["loss_spans"][-1]
            final = row["text"][a:b]
            c = info.setdefault(base, {"id": base, "source": meta["source"], "seeded": meta["seeded_from_test"],
                                       "tools": set(), "finals": [], "multi": False, "zero": False,
                                       "family": meta["case_tags"].get("family"),
                                       "scenario": meta["case_tags"].get("scenario")})
            c["tools"].update(meta["traj"]["tool_seq"])
            if tool_name(final) is None:
                c["finals"].append(final)
            c["multi"] |= meta["traj"]["turns_total"] > 1
            if meta["turn"] == 1 and meta["traj"]["zero_call"]:
                c["zero"] = True
    return info


def case_dirs():
    dirs = {}
    for path in glob.glob(os.path.join(DISTILL, "v1*", "cases", "*", "*", "case.json")):
        dirs[os.path.basename(os.path.dirname(path))] = os.path.dirname(path)
    return dirs


def new_id(old):
    prefix, number = old.rsplit("-", 1)
    assert len(number) == 4, old
    return "%s-2%s" % (prefix, number)


def policy_for(c, case):
    must = set(c["tools"])
    for turn in case["turns"]:
        e = turn.get("expect", {})
        must.update(e.get("required_tools") or [])
        must.update(e.get("forbidden_tools") or [])
        for call in (e.get("calls") or []) + (e.get("required_calls") or []):
            if call.get("name"):
                must.add(call["name"])
    never = set()
    if case.get("offered_tools") is not None:
        never = set(WORK_V1) - set(case["offered_tools"])
    must -= never
    must &= set(WORK_V2)
    order = {name: i for i, name in enumerate(WORK_V2)}
    policy = {}
    if must:
        policy["must_offer"] = sorted(must, key=order.get)
    if never:
        policy["never_offer"] = sorted(never, key=order.get)
    return policy


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--n", type=int, default=600)
    ap.add_argument("--report", default=os.path.join(DISTILL, "v2.0", "reports", "b20s-selection.json"))
    args = ap.parse_args()

    info, dirs = load_pool(), case_dirs()
    pool, dropped = [], collections.Counter()
    for cid in sorted(info):
        c = info[cid]
        if c["seeded"] or c["source"] == "base700":
            dropped["seeded_from_test"] += 1
            continue
        if cid not in dirs:
            dropped["case_dir_missing"] += 1
            continue
        if any(len(f) > 400 for f in c["finals"]):
            dropped["final_over_400"] += 1
            continue
        if any(MD.search(f) for f in c["finals"]):
            dropped["final_markdown"] += 1
            continue
        verify = os.path.join(dirs[cid], "verify.py")
        if os.path.exists(verify) and "offered_tools" in open(verify, encoding="utf-8").read():
            # verify.py asserts the authored fixed directory; v2.0 draws it.
            dropped["verify_pins_offered_tools"] += 1
            continue
        case = json.load(open(os.path.join(dirs[cid], "case.json"), encoding="utf-8"))
        c["case"] = case
        c["zh"] = bool(CJK.search(case["turns"][0]["prompt"]))
        c["b12"] = c["source"].startswith("distill-b12")
        pool.append(c)

    rng = random.Random(SEED)
    rng.shuffle(pool)
    chosen, families = [], set()

    def take(pred, quota):
        got = 0
        for c in pool:
            if got >= quota or len(chosen) >= args.n:
                break
            if c["family"] in families or c in chosen or not pred(c):
                continue
            chosen.append(c)
            families.add(c["family"])
            got += 1
        return got

    take(lambda c: c["b12"], 90)
    take(lambda c: not c["b12"] and c["multi"], 120)
    take(lambda c: not c["b12"] and not c["multi"] and c["zero"], 120)
    scen = collections.Counter(c["scenario"] for c in pool)
    cap = {s: int(1.5 * args.n / len(scen)) for s in scen}
    have = collections.Counter(c["scenario"] for c in chosen)
    for c in pool:
        if len(chosen) >= args.n:
            break
        if c in chosen or c["family"] in families or have[c["scenario"]] >= cap[c["scenario"]]:
            continue
        chosen.append(c)
        families.add(c["family"])
        have[c["scenario"]] += 1

    out_root = cases_dir("v2.0")
    hidden_limits = [0]
    for old in glob.glob(os.path.join(out_root, "*", "*", "case.json")):
        if json.load(open(old, encoding="utf-8")).get("tags", {}).get("batch") == "b20s":
            shutil.rmtree(os.path.dirname(old))
    for c in sorted(chosen, key=lambda c: c["id"]):
        nid = new_id(c["id"])
        case = json.loads(json.dumps(c["case"]))
        src_dir = dirs[c["id"]]
        dst_dir = os.path.join(out_root, case["category"], nid)
        if os.path.exists(dst_dir):
            shutil.rmtree(dst_dir)
        shutil.copytree(src_dir, dst_dir)
        rebuilt = {}
        for key, value in case.items():
            if key == "offered_tools":
                continue
            rebuilt[key] = nid if key == "id" else value
        for turn in rebuilt["turns"]:
            expect = turn.get("expect", {})
            if "max_output_chars" in expect and not LENGTH_CUE.search(turn["prompt"]):
                # A hidden length limit the 1.x suffix used to satisfy; the
                # v2.0 teacher has no suffix, and filter.py caps finals at 600.
                del expect["max_output_chars"]
                hidden_limits[0] += 1
        tags = rebuilt["tags"]
        tags["tool_catalog"] = "work-v2"
        tags["batch"] = "b20s"
        tags["derived_from"] = c["id"]
        policy = policy_for(c, case)
        if policy:
            rebuilt["tool_policy"] = policy
        with open(os.path.join(dst_dir, "case.json"), "w", encoding="utf-8") as f:
            json.dump(rebuilt, f, ensure_ascii=False, indent=2)
            f.write("\n")

    n = len(chosen)
    stats = {
        "pool": len(pool), "dropped": dict(dropped), "chosen": n,
        "b12": sum(c["b12"] for c in chosen),
        "multi_turn": sum(c["multi"] for c in chosen),
        "zero_call_first_turn": sum(c["zero"] for c in chosen),
        "zh": sum(c["zh"] for c in chosen),
        "families": len(families),
        "scenario": dict(sorted(collections.Counter(c["scenario"] for c in chosen).items())),
        "source": dict(sorted(collections.Counter(c["source"] for c in chosen).items())),
        "hidden_max_output_chars_removed": hidden_limits[0],
        "with_never_offer": sum(bool(policy_for(c, c["case"]).get("never_offer")) for c in chosen),
        "ids": sorted(new_id(c["id"]) + "<-" + c["id"] for c in chosen),
    }
    os.makedirs(os.path.dirname(args.report), exist_ok=True)
    with open(args.report, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(json.dumps({k: v for k, v in stats.items() if k != "ids"}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()

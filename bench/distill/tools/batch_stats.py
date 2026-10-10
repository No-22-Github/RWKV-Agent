#!/usr/bin/env python3
"""Every number in reports/<batch>.md, recomputed from the artifacts (read-only),
for b10b onward (b10a keeps tools/b10a/report_stats.py).

  python3 bench/distill/tools/<batch>/report_stats.py     # from repo root

Callers pass the batch id and SUB = {module: [(prefix, lo, hi), ...]}. Inputs:
live/shelved cases, teacher runs under local/runs/distill/v141/<batch>
(teacher-k0..2 for v1 cases, fix-k0..2 for the v2 re-runs), the paths reports,
bench/distill/v1.4/teacher/<batch>.jsonl, corpus/rows.jsonl and the exclude list.
"""
import collections
import glob
import json
import os
import re

CJK = re.compile(r"[一-鿿]")
WAIT = re.compile(r"\b(Wait|Hmm|Actually|But wait)\b")


def _q(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(len(xs) * p))] if xs else 0


def _summary(run):
    return {c["id"]: c for c in json.load(open(os.path.join(run, "summary.json")))["cases"]}


def _passk(runs, ids):
    d = collections.Counter(sum(1 for r in runs if r.get(c, {}).get("passed")) for c in ids)
    return {f"{n}/3": d[n] for n in (3, 2, 1, 0)}


def stats(batch, SUB, shelved):
    R = "local/runs/distill/v141/" + batch

    def sub(cid):
        s, n = cid.split("-")
        for k, v in SUB.items():
            if any(a == s and lo <= int(n) <= hi for a, lo, hi in v):
                return k

    live = {}
    for p in glob.glob("bench/distill/v1.4/cases/*/*/case.json"):
        c = json.load(open(p))
        if c["tags"]["author"].endswith("-" + batch):
            live[c["id"]] = c
    v2 = sorted(c for c in live if live[c]["tags"]["version"] == 2)
    out = {"drafted": len(live) + len(shelved), "live": len(live), "shelved": len(shelved), "v2": len(v2),
           "zh_cases": sum(bool(CJK.search(" ".join(t["prompt"] for t in c["turns"]))) for c in live.values())}
    orig = [_summary(f"{R}/teacher-k{k}") for k in range(3)]
    out["pass_first"] = _passk(orig, sorted(orig[0]))
    fix = [_summary(f"{R}/fix-k{k}") for k in range(3)] if os.path.isdir(f"{R}/fix-k0") else []
    if fix:
        out["pass_v2_rerun"] = _passk(fix, sorted(fix[0]))
    d = collections.Counter(sum(1 for r in (fix if c in v2 else orig) if r.get(c, {}).get("passed")) for c in live)
    out["pass_final_live"] = {f"{n}/3": d[n] for n in (3, 2, 1, 0)}

    drops = collections.Counter()
    for name, isfix in (("paths-orig-report.jsonl", False), ("paths-fix-report.jsonl", True)):
        if not os.path.exists(f"{R}/{name}"):
            continue
        for line in open(f"{R}/{name}"):
            r = json.loads(line)
            cid = r["case_id"]
            if cid in live and (cid in v2) == isfix:
                drops.update(r["drops"])
    out["paths_drops_live"] = dict(drops)

    script = [json.loads(l) for l in open(f"bench/distill/v1.4/teacher/{batch}.jsonl")]
    excl = {}
    for l in open("bench/distill/common/exclude.jsonl"):
        if l.strip():
            e = json.loads(l)
            if e.get("batch") == batch:
                excl[e["case_id"]] = e["reason"]
    kept_paths = [s for s in script if s["case_id"] not in excl]
    out["paths_in_script"] = len(script)
    out["paths_excluded"] = len(excl)
    reasons = collections.Counter()
    for r in excl.values():
        reasons["oversize" if "打包上限" in r else "bare value" if "裸值" in r else "DONE leak" if "DONE" in r else "manual"] += 1
    out["exclude_reasons"] = dict(reasons)

    rows = [json.loads(l) for l in open(f"{R}/corpus/rows.jsonl")]
    out["rows_rendered"] = len(rows)
    out["wire_hash"] = sorted({r["meta"]["wire_hash"] for r in rows})
    krows = [r for r in rows if r["meta"]["case_id"] not in excl]
    out["rows_kept"] = len(krows)

    per = collections.defaultdict(collections.Counter)
    for c in live:
        per[sub(c)]["live"] += 1
    for c in shelved:
        per[sub(c)]["shelved"] += 1
    covered = collections.defaultdict(set)
    zh_rows = 0
    for r in krows:
        cid = r["meta"]["case_id"].split("--")[0]
        k = sub(cid)
        per[k]["rows"] += 1
        covered[k].add(cid)
        zh = bool(CJK.search(live[cid]["turns"][r["meta"]["turn"] - 1]["prompt"]))
        per[k]["zh_rows"] += zh
        zh_rows += zh
    for k in per:
        per[k]["cases_with_rows"] = len(covered[k])
    out["per_module"] = {k: dict(per[k]) for k in sorted(per)}
    out["zh_rows"] = f"{zh_rows}/{len(krows)}"

    finals = []
    for r in krows:
        a, b = r["loss_spans"][-1]
        finals.append(r["text"][a:b].strip())
    calls = collections.Counter()
    first_list = with_tool = zero = 0
    for r in krows:
        seq = r["meta"]["traj"]["tool_seq"]
        calls.update(seq)
        zero += r["meta"]["traj"]["zero_call"]
        if seq:
            with_tool += 1
            first_list += seq[0] == "list_files"
    total = sum(calls.values())
    lens = [len(f) for f in finals]
    out["composition"] = {
        "pure_value_finals": f"{sum(len(f) <= 12 for f in finals)}/{len(krows)}",
        "data_query_share": f"{calls['data_query']}/{total}",
        "calculator_calls": calls["calculator"],
        "first_action_list_files": f"{first_list}/{with_tool}",
        "zero_call_rows": f"{zero}/{len(krows)}",
        "final_len_p50": _q(lens, 0.5), "final_len_max": max(lens),
        "tool_calls_by_name": dict(calls.most_common()),
    }

    steps = think = over = wait = 0
    first, later, zh_flags = [], [], []
    for s in kept_paths:
        cid = s["case_id"].split("--")[0]
        zh_case = any(CJK.search(t["prompt"]) for t in live[cid]["turns"])
        for i, o in enumerate(s["outputs"]):
            steps += 1
            t = o.get("reasoning") or ""
            if not t:
                continue
            think += 1
            (first if i == 0 else later).append(len(t))
            over += len(t) > 900
            wait += bool(WAIT.search(t))
            if zh_case:
                zh_flags.append(len(CJK.findall(t)) > 0.2 * len(t))
    out["thinking"] = {
        "outputs_with_thinking": f"{think}/{steps}",
        "first_p50_p90": [_q(first, 0.5), _q(first, 0.9)],
        "later_p50_p90": [_q(later, 0.5), _q(later, 0.9)],
        "over_900": f"{over}/{think}",
        "wait_hmm_actually": f"{wait}/{think}",
        "zh_case_thinking_in_zh": f"{sum(zh_flags)}/{len(zh_flags)}",
    }
    out["shelved_reasons"] = shelved
    out["uncovered_live_cases"] = sorted(c for c in live if not any(c in covered[k] for k in covered))
    print(json.dumps(out, ensure_ascii=False, indent=1))

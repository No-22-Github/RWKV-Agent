#!/usr/bin/env python3
"""Every number in reports/b10a.md, recomputed from the artifacts (read-only).

  python3 bench/distill/tools/b10a/report_stats.py            # from repo root

Inputs: the live/shelved cases, teacher runs under local/runs/distill/v141/b10a
(teacher-k0..2 for v1 cases, fix-k0..2 for the v2 re-runs), the paths reports,
bench/distill/v1.4/teacher/b10a.jsonl, corpus/rows.jsonl and the exclude list.
"""
import collections
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
os.chdir(ROOT)
sys.path.insert(0, "bench/distill/tools/b10a")
from common import SHELVED  # noqa: E402

RUN = "local/runs/distill/v141/b10a"
SMOKE = "local/runs/distill/v141/smoke"
SUB = {'m2a': [('cfg', 8012, 8021), ('doc', 8006, 8013)], 'm2b': [('fs', 8004, 8011), ('log', 8010, 8017)],
       'm2c': [('tab', 8016, 8027), ('web', 8013, 8020), ('code', 8004, 8009)],
       'm2d': [('cfg', 8022, 8031), ('log', 8018, 8027), ('tab', 8028, 8033), ('doc', 8014, 8019), ('fs', 8012, 8019)],
       'm2e': [('web', 8021, 8035), ('hyb', 8006, 8020)],
       'm2f': [('tab', 8034, 8041), ('log', 8028, 8033), ('doc', 8020, 8022), ('fs', 8020, 8022)],
       'm3a': [('cfg', 8032, 8039), ('fs', 8023, 8028), ('log', 8034, 8041), ('tab', 8042, 8051), ('doc', 8023, 8030)],
       'm3b': [('nt', 8011, 8040), ('doc', 8031, 8040), ('cfg', 8040, 8049)],
       'm3c': [('tab', 8052, 8057), ('log', 8042, 8047), ('cfg', 8050, 8053), ('fs', 8029, 8032), ('nt', 8041, 8045)]}
NAME = {'m2a': 'M2 诱饵（cfg/doc）', 'm2b': 'M2 诱饵（fs/log）', 'm2c': 'M2 诱饵（tab/web/code）', 'm2d': 'M2 缺项',
        'm2e': 'M2 网页失败', 'm2f': 'M2 部分可答', 'm3a': 'M3 两轮复述', 'm3b': 'M3 单轮禁令', 'm3c': 'M3 反问点名参数'}
CJK = re.compile(r"[一-鿿]")
WAIT = re.compile(r"\b(Wait|Hmm|Actually|But wait)\b")


def sub(cid):
    s, n = cid.split("-")
    for k, v in SUB.items():
        if any(a == s and lo <= int(n) <= hi for a, lo, hi in v):
            return k


def q(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(len(xs) * p))] if xs else 0


def summary(run):
    return {c["id"]: c for c in json.load(open(os.path.join(run, "summary.json")))["cases"]}


def passk(runs, ids):
    d = collections.Counter(sum(1 for r in runs if r.get(c, {}).get("passed")) for c in ids)
    return {f"{n}/3": d[n] for n in (3, 2, 1, 0)}


live = {}
for p in glob.glob("bench/distill/v1.4/cases/*/*/case.json"):
    c = json.load(open(p))
    if c["tags"]["author"].endswith("b10a"):
        live[c["id"]] = c
shelved = sorted(SHELVED)
v2 = sorted(c for c in live if live[c]["tags"]["version"] == 2)
out = {"drafted": len(live) + len(shelved), "live": len(live), "shelved": len(shelved), "v2": len(v2)}

orig = [summary(f"{RUN}/teacher-k{k}") for k in range(3)]
fix = [summary(f"{RUN}/fix-k{k}") for k in range(3)]
out["pass_orig_265"] = passk(orig, sorted(orig[0]))
out["pass_fix_84"] = passk(fix, sorted(fix[0]))
final_verdict = {c: (fix if c in v2 else orig) for c in live}
out["pass_final_live"] = passk([], [])  # placeholder replaced below
d = collections.Counter(sum(1 for r in final_verdict[c] if r.get(c, {}).get("passed")) for c in live)
out["pass_final_live"] = {f"{n}/3": d[n] for n in (3, 2, 1, 0)}

drops = collections.Counter()
for name, ids in (("paths-orig-report.jsonl", None), ("paths-fix-report.jsonl", None)):
    for line in open(f"{RUN}/{name}"):
        r = json.loads(line)
        cid = r["case_id"]
        if cid not in live or (cid in v2) != (name.startswith("paths-fix")):
            continue
        drops.update(r["drops"])
out["paths_drops_live"] = dict(drops)

script = [json.loads(l) for l in open("bench/distill/v1.4/teacher/b10a.jsonl")]
excluded = {json.loads(l)["case_id"] for l in open("bench/distill/common/exclude.jsonl") if l.strip()}
kept_paths = [s for s in script if s["case_id"] not in excluded]
out["paths_in_script"] = len(script)
out["paths_excluded"] = len([s for s in script if s["case_id"] in excluded])

rows = [json.loads(l) for l in open(f"{RUN}/corpus/rows.jsonl")]
out["rows_rendered"] = len(rows)
out["wire_hash"] = sorted({r["meta"]["wire_hash"] for r in rows})
krows = [r for r in rows if r["meta"]["case_id"] not in excluded]
out["rows_kept"] = len(krows)

per = collections.defaultdict(lambda: collections.Counter())
for c in live:
    per[sub(c)]["live"] += 1
for c in shelved:
    per[sub(c)]["shelved"] += 1
covered = collections.defaultdict(set)
for r in krows:
    cid = r["meta"]["case_id"].split("--")[0]
    k = sub(cid)
    per[k]["rows"] += 1
    covered[k].add(cid)
    prompt = live[cid]["turns"][r["meta"]["turn"] - 1]["prompt"]
    per[k]["zh_rows"] += bool(CJK.search(prompt))
for k in per:
    per[k]["cases_with_rows"] = len(covered[k])
out["per_class"] = {k: dict(per[k]) for k in sorted(per)}
for grp in ("m2", "m3"):
    rr = [r for r in krows if sub(r["meta"]["case_id"].split("--")[0]).startswith(grp)]
    zh = sum(bool(CJK.search(live[r["meta"]["case_id"].split("--")[0]]["turns"][r["meta"]["turn"] - 1]["prompt"])) for r in rr)
    out[f"{grp}_rows"] = len(rr)
    out[f"{grp}_zh_rows"] = zh


def final_text(r):
    a, b = r["loss_spans"][-1]
    return r["text"][a:b].strip()


finals = [final_text(r) for r in krows]
pure = [f for f in finals if len(f) <= 12]
calls = collections.Counter()
first_list = with_tool = zero = 0
for r in krows:
    seq = r["meta"]["traj"]["tool_seq"]
    calls.update(seq)
    zero += r["meta"]["traj"]["zero_call"]
    if seq:
        with_tool += 1
        first_list += seq[0] == "list_files"
total_calls = sum(calls.values())
lens = [len(f) for f in finals]
out["composition"] = {
    "pure_value_finals": f"{len(pure)}/{len(krows)}",
    "data_query_share": f"{calls['data_query']}/{total_calls}",
    "calculator_calls": calls["calculator"],
    "first_action_list_files": f"{first_list}/{with_tool}",
    "zero_call_rows": f"{zero}/{len(krows)}",
    "final_len_p50": q(lens, 0.5), "final_len_max": max(lens),
    "tool_calls_by_name": dict(calls.most_common()),
}

# thinking stats over kept paths (reasoning recorded per output in the script)
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
    "first_p50_p90": [q(first, 0.5), q(first, 0.9)],
    "later_p50_p90": [q(later, 0.5), q(later, 0.9)],
    "over_900": f"{over}/{think}",
    "wait_hmm_actually": f"{wait}/{think}",
    "zh_case_thinking_in_zh": f"{sum(zh_flags)}/{len(zh_flags)}",
}

smoke = {}
for name in ("pilot-suffix", "pilot-nosuffix", "b12-suffix-r2", "b12-nosuffix-r2"):
    s = summary(f"{SMOKE}/{name}")
    smoke[name] = f"{sum(1 for c in s.values() if c.get('passed'))}/{len(s)}"
out["smoke_pass"] = smoke
out["shelved_reasons"] = SHELVED
out["uncovered_live_cases"] = sorted(c for c in live if not any(c in covered[k] for k in covered))
print(json.dumps(out, ensure_ascii=False, indent=1))

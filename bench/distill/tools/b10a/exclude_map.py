#!/usr/bin/env python3
"""Map the S5 reading verdicts onto the teacher script's path ids (b10a).

Verdicts are keyed by (case, run set, k) — which run produced the path — so
they survive re-running `corpus paths` (path ids --pN can shift). Writes the
b10a lines of bench/distill/common/exclude.jsonl (other batches untouched).
Also drops paths whose final answer is a bare value the prompt did not ask
for (v1.4 §4.2). Run from the repo root after corpus paths, before render.
"""
import glob
import json
import re

R = "local/runs/distill/v141/b10a"
MANUAL = {
    ("tab-8019", "orig", 0): "把继任桥滨江桥的合计当成青石桥的答案",
    ("web-8013", "orig", 1): "终答末尾泄漏「DONE? No — user didn't ask…」自言自语",
    ("tab-8025", "orig", 0): "整读 rides 表后不用工具报出 Swift-10 骑行数（心算）",
    ("log-8012", "orig", 1): "复述诱饵数值（备用泵的 3 条告警）",
    ("log-8017", "orig", 1): "复述诱饵数值（手动导入批次 7 单、4 单）",
    ("log-8017", "orig", 2): "复述诱饵数值（手动导入批次 7 单、4 单）",
    ("hyb-8010", "orig", 1): "复述过时二手单价「18 元/瓶」",
    ("fs-8021", "fix", 2): "把已归档 57 份当成 9 月总数，没标明不完整",
    ("log-8043", "fix", 1): "第 1 轮反问问的是文件路径与字段，没问缺的日期范围",
}
OVERSIZE = {("fs-8021", "fix", 0): "渲染后 9647 token，超过 8128 打包上限（逐个读取几十个许可文件）"}
ONLY_VALUE = re.compile(r"只回|只给|只要数字|only the (number|answer|value)|Reply with only")

cases = {}
for p in glob.glob("bench/distill/v1.4/cases/*/*/case.json"):
    c = json.load(open(p))
    cases[c["id"]] = c
runs = {}
for src, name in (("orig", "teacher"), ("fix", "fix")):
    for k in range(3):
        runs[(src, k)] = {c["id"]: c for c in json.load(open(f"{R}/{name}-k{k}/summary.json"))["cases"]}


def finals(c):
    return [((t.get("result") or {}).get("output") or "").strip() for t in c["turns"]]


excl = []
for line in open("bench/distill/v1.4/teacher/b10a.jsonl"):
    d = json.loads(line)
    pid = d["case_id"]
    cid = pid.split("--")[0]
    src = "fix" if cases[cid]["tags"]["version"] == 2 else "orig"
    fins = [o["text"].strip() for o in d["outputs"] if not o["text"].startswith("<tool_call>")]
    hits = [k for k in range(3) if runs[(src, k)].get(cid, {}).get("passed") and finals(runs[(src, k)][cid]) == fins]
    assert hits, pid
    reason = next((v for k in hits for key, v in list(MANUAL.items()) + list(OVERSIZE.items()) if key == (cid, src, k)), None)
    if not reason:
        for ti, f in enumerate(fins):
            if len(f) <= 8 and not ONLY_VALUE.search(cases[cid]["turns"][ti]["prompt"]):
                reason = "第 %d 轮只给裸值「%s」，题面没要求只回数值（§4.2）" % (ti + 1, f)
                break
    if reason:
        excl.append({"batch": "b10a", "case_id": pid, "reason": reason})

path = "bench/distill/common/exclude.jsonl"
keep = [l for l in open(path) if l.strip() and json.loads(l).get("batch") != "b10a"]
with open(path, "w") as f:
    f.writelines(keep)
    for e in excl:
        f.write(json.dumps(e, ensure_ascii=False) + "\n")
for e in excl:
    print(e["case_id"], e["reason"])
print(len(excl), "b10a paths excluded")

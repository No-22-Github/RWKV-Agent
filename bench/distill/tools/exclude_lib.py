"""Map S5 reading verdicts onto a batch's teacher script path ids (b10b onward;
b10a keeps its own copy in tools/b10a/exclude_map.py).

Verdicts are keyed by (case, run set, k) — which run produced the path — so
they survive re-running `corpus paths` (path ids --pN can shift). Rewrites the
batch's lines of bench/distill/common/exclude.jsonl (other batches untouched).
Also drops paths whose final answer is a bare value the prompt did not ask for
(v1.4 §4.2). Run from the repo root after corpus paths, before render.
"""
import glob
import json
import re

ONLY_VALUE = re.compile(r"只回|只给|只要|only the (number|answer|value)|[Rr]eply with only|just the number|number only|value only")


def _finals(c):
    return [((t.get("result") or {}).get("output") or "").strip() for t in c["turns"]]


def run(batch, manual, oversize=None):
    R = "local/runs/distill/v141/" + batch
    verdicts = list(manual.items()) + list((oversize or {}).items())
    cases = {}
    for p in glob.glob("bench/distill/v1.4/cases/*/*/case.json"):
        c = json.load(open(p))
        cases[c["id"]] = c
    runs = {}
    for src, name in (("orig", "teacher"), ("fix", "fix")):
        for k in range(3):
            try:
                runs[(src, k)] = {c["id"]: c for c in json.load(open(f"{R}/{name}-k{k}/summary.json"))["cases"]}
            except FileNotFoundError:
                pass
    excl, used = [], set()
    for line in open(f"bench/distill/v1.4/teacher/{batch}.jsonl"):
        d = json.loads(line)
        pid = d["case_id"]
        cid = pid.split("--")[0]
        src = "fix" if cases[cid]["tags"]["version"] == 2 else "orig"
        fins = [o["text"].strip() for o in d["outputs"] if not o["text"].startswith("<tool_call>")]
        hits = [k for k in range(3) if runs.get((src, k), {}).get(cid, {}).get("passed")
                and _finals(runs[(src, k)][cid]) == fins]
        assert hits, pid
        reason = None
        for key, v in verdicts:
            if key[0] == cid and key[1] == src and key[2] in hits:
                reason = v
                used.add(key)
                break
        if not reason:
            for ti, f in enumerate(fins):
                if len(f) <= 8 and not ONLY_VALUE.search(cases[cid]["turns"][ti]["prompt"]):
                    reason = "第 %d 轮只给裸值「%s」，题面没要求只回数值（§4.2）" % (ti + 1, f)
                    break
        if reason:
            excl.append({"batch": batch, "case_id": pid, "reason": reason})
    unused = [k for k, _ in verdicts if k not in used]
    assert not unused, ("verdicts matched no kept path", unused)
    path = "bench/distill/common/exclude.jsonl"
    keep = [l for l in open(path) if l.strip() and json.loads(l).get("batch") != batch]
    with open(path, "w") as f:
        f.writelines(keep)
        for e in excl:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    for e in excl:
        print(e["case_id"], e["reason"])
    print(len(excl), batch, "paths excluded")

"""Shared writer for the b10 pilot cases (v1.4 M2 milestone).

Each case is written as bench/distill/cases/<scenario>/<id>/{case.json,verify.py,NOTES.md}.
The canary is derived from the case id so re-running a builder is idempotent.
"""
import hashlib
import json
import os

REPO = "/Users/no22/Projects/RWKV-Agent"
CASES = os.path.join(REPO, "bench", "distill", "cases")
AUTHOR = "llm:claude-opus-5-5-b10"

SCEN = {"tab": "tabular", "log": "logs", "cfg": "config", "doc": "docs", "fs": "filesystem",
        "scr": "script", "code": "code", "web": "web", "hyb": "hybrid", "nt": "notool"}


def canary(cid):
    return "DISTILL-CANARY-" + hashlib.sha256(("b10-pilot:" + cid).encode()).hexdigest()[:8]


def write_case(cid, *, desc, task_type, family, level, ref_calls, files, turns,
               traps=(), decoys=None, axes=(), web=None, offered_tools=None,
               case_expect=None, verify, notes, answer_style="natural", version=1):
    abbrev = cid.split("-")[0]
    scenario = SCEN[abbrev]
    can = canary(cid)
    case = {
        "id": cid,
        "description": desc.rstrip(".") + ". " + can,
        "category": scenario,
        "tags": {
            "scenario": scenario,
            "task_type": task_type,
            "traps": list(traps),
            "trap_decoys": dict(decoys or {}),
            "axes": list(axes),
            "level": level,
            "family": family,
            "ref_calls": ref_calls,
            "fixture_bytes": sum(len(v.encode()) for v in files.values()),
            "status": "draft",
            "version": version,
            "author": AUTHOR,
            "reviewer": None,
            "answer_style": answer_style,
        },
        "web_fixture": list(web or []),
        "files": files,
        "turns": turns,
    }
    if offered_tools is not None:
        case["offered_tools"] = list(offered_tools)
    if case_expect:
        case["expect"] = case_expect
    d = os.path.join(CASES, scenario, cid)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "case.json"), "w") as f:
        json.dump(case, f, ensure_ascii=False, indent=2)
        f.write("\n")
    with open(os.path.join(d, "verify.py"), "w") as f:
        f.write("# %s : distillation case\n" % can)
        f.write(verify.strip("\n") + "\n")
    with open(os.path.join(d, "NOTES.md"), "w") as f:
        f.write(notes.strip("\n") + "\n")
    return d


def csv_text(header, rows):
    out = [",".join(header)]
    for r in rows:
        out.append(",".join(str(x) for x in r))
    return "\n".join(out) + "\n"

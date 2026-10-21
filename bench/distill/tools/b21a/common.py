"""b21a (v2.1: editing existing files) shared framework.

A case is: fixture files + per-turn edit ops. Ops are applied cumulatively to
the fixture; the final tree is the expect.files truth (equals for changed
files, unchanged for the rest). verify.py replays the same ops from case.json.
Op forms: ("sub", path, old, new)  old must occur exactly once;
          ("app", path, text)      text appended to the end of the file.
"""
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from casegen import Batch  # noqa: E402

# tool policies
RW = {"must_offer": ["read_file", "write_file"], "never_offer": ["web_search", "web_fetch"]}
RL = {"must_offer": ["read_lines", "replace_lines"], "never_offer": ["web_search", "web_fetch"]}
RA = {"must_offer": ["read_file", "append_file"], "never_offer": ["web_search", "web_fetch"]}
RB = {"must_offer": ["bash"], "never_offer": ["web_search", "web_fetch"]}
RLW = {"must_offer": ["read_lines", "write_file"], "never_offer": ["web_search", "web_fetch"]}

BATCH = Batch(salt="b21a", author="llm:claude-sonnet-b21a", version="v2.1", tool_catalog="agent-tool-v2.0")
EXTRA = {"batch": "b21a"}
META = {}

APPLY_SRC = '''
def apply(files, ops):
    out = dict(files)
    for op in ops:
        if op[0] == "sub":
            _, path, old, new = op
            assert out[path].count(old) == 1, (path, old)
            out[path] = out[path].replace(old, new)
        elif op[0] == "app":
            out[op[1]] = out[op[1]] + op[2]
    return out
'''
_ns = {}
exec(APPLY_SRC, _ns)
apply_ops = _ns["apply"]


def is_zh(text):
    return len(re.findall(r"[一-鿿]", text)) >= 4


def level_for(n_traps, ref_calls, n_files, multi):
    if n_traps == 0 and ref_calls <= 3:
        return "L0"
    if n_traps == 1 and ref_calls <= 4 and not multi:
        return "L1"
    if n_traps == 2 or (n_traps == 1 and (n_files >= 3 or ref_calls >= 5)):
        return "L2"
    if n_traps >= 1 and multi:
        return "L3"
    if n_traps >= 3 or ref_calls >= 8:
        return "L3"
    return "L1"


def guard(files):
    d = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    return ("import hashlib, json\n"
            "case = json.load(open(\"case.json\"))\n"
            "_pin = hashlib.sha256(json.dumps(case[\"files\"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()\n"
            "assert _pin == %r, \"fixture changed\"\n" % d)


def make(cid, *, sub, task_type, desc, files, turns, ops, notes_ref, traps=("TR-DECOY",), policy=None,
         ref_calls=4, axes=("OBS", "VER"), loose=None):
    """turns: list of (prompt, output_contains list, output_excludes list).
    ops: list (per turn) of op lists. keep: files to mark unchanged (default: all untouched)."""
    allops = [o for t in ops for o in t]
    end = apply_ops(files, allops)
    rules = {}
    for p, t in files.items():
        if loose and p in loose:
            rules[p] = {"contains": [t] + list(loose[p])}
        else:
            rules[p] = {"equals": end[p]} if end[p] != t else {"unchanged": True}
    assert any("equals" in r or "contains" in r for r in rules.values()), cid
    if loose:
        for p, subs in loose.items():
            assert all(x in end[p] for x in [files[p]] + list(subs)), (cid, p)
    tl = []
    for prompt, inc, exc in turns:
        e = {}
        inc = [x for x in (inc or []) if len(x) > 1 and not re.fullmatch(r"\d{1,3}(\.\d{1,2})?", x)]
        if inc:
            e["output_contains"] = list(inc)
        if exc:
            e["output_excludes"] = list(exc)
        tl.append({"prompt": prompt, "expect": e})
    for p in files:
        assert end[p].endswith("\n") == files[p].endswith("\n"), (cid, p)
    if policy is None:
        opts = [RA, RW, RB] if sub == "append" else [RW, RL, RB, RLW]
        policy = opts[int(cid.split("-")[1]) % len(opts)]
    multi = len(turns) > 1
    if "TR-READONLY" in traps and "CON" not in axes:
        axes = tuple(axes) + ("CON",)
    level = level_for(len(traps), ref_calls, len(files), multi)
    body = APPLY_SRC + "\nOPS = json.loads(%r)\nend = apply(case[\"files\"], OPS)\n" % json.dumps(allops, ensure_ascii=False)
    body += "print(json.dumps({\"files\": {p: t for p, t in end.items() if case[\"files\"][p] != t}}, ensure_ascii=False))\n"
    n_changed = sum(1 for r in rules.values() if "unchanged" not in r)
    notes = "## Traps\n" + "".join("- %s\n" % t for t in notes_ref["traps"])
    notes += "- %d file(s) change, %d stay byte-identical.\n" % (n_changed, len(rules) - n_changed)
    notes += "\n## Reference solution\n" + "".join("%d. %s\n" % (i, s) for i, s in enumerate(notes_ref["steps"], 1))
    notes += "\n## Why the answer is unique\n" + notes_ref["unique"] + "\n"
    notes += "Final answer should mention: %s\n" % "; ".join(x for _, inc, _ in turns for x in (inc or []))
    fam = "b21a-%s-%s" % (sub, cid.split("-")[1])
    BATCH.write_case(cid, desc=desc, task_type=task_type, family=fam, level=level, ref_calls=ref_calls, files=files,
                     turns=tl, verify=guard(files) + body, notes=notes, traps=list(traps),
                     decoys={t: None for t in traps}, axes=list(axes), case_expect={"files": rules},
                     answer_style="natural", tool_policy=policy, extra_tags=EXTRA)
    META[cid] = {"sub": sub, "lang": "zh" if is_zh(" ".join(t[0] for t in turns)) else "en",
                 "turns": len(turns), "policy": bool(policy), "level": level}


def L(*rows):
    return "".join(r + "\n" for r in rows)


"""b23g (v2.3: the answer is past the first screen of a long file, ids 35501-35540).

make() takes one long fixture file (lines already composed) and turns; every turn names the planted
answer line (`line`) and, for G1, a similar-but-wrong decoy line that is visible on the first screen.
Build-time asserts: G1 answer line > 230 and decoy line < 150; G0 answer line < 60 and the deep
look-alike line > 230. verify.py re-checks the same facts from the fixture.
"""
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from casegen import Batch  # noqa: E402

BATCH = Batch(salt="b23g", author="llm:claude-sonnet-b23g", version="v2.3", tool_catalog="agent-tool-v3.2")
META = {}
HAN = re.compile(r"[一-鿿]")
POL = {"must_offer": ["read_file", "search_text"], "never_offer": ["web_search", "web_fetch", "bash"]}
TT = {"doc": "policy_lookup", "log": "locate_error", "cfg": "read_effective", "code": "locate_definition"}
POL0 = {"must_offer": ["read_file"], "never_offer": ["web_search", "web_fetch", "bash"]}


def is_zh(t):
    return len(HAN.findall(t)) >= 4


def forms_int(v):
    s = str(v)
    out = [s]
    if v >= 1000:
        out.append("{:,}".format(v))
    return out


def guard(files):
    d = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    return ("import hashlib, json\n"
            "case = json.load(open(\"case.json\"))\n"
            "files = case[\"files\"]\n"
            "_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()\n"
            "assert _pin == %r, \"fixture changed\"\n" % d)


def find(lines, sub):
    hits = [i + 1 for i, l in enumerate(lines) if sub in l]
    assert len(hits) == 1, (sub, hits)
    return hits[0]


def T(q, ans, line, decoy=None, excl=(), deep=None):
    """ans: str | int | ("any", [forms]); line: unique substring of the planted answer line;
    decoy: unique substring of the first-screen decoy line (G1); deep: unique substring of the deep look-alike (G0)."""
    return dict(q=q, ans=ans, line=line, decoy=decoy, excl=list(excl), deep=deep)


def make(cid, *, sub, task_type, desc, path, lines, turns, notes, policy=None, ref_calls=3, extra=None):
    g1 = sub == "G1"
    body = "\n".join(lines) + "\n"
    files = {path: body}
    if extra:
        files.update(extra)
    n = len(lines)
    if g1:
        assert 300 <= n <= 1500, (cid, n)
    else:
        assert n >= 300, (cid, n)
    assert max(len(l) for l in lines) <= 120, cid
    tl = []
    facts = []
    for t in turns:
        al = find(lines, t["line"])
        e = {}
        a = t["ans"]
        if isinstance(a, tuple):
            e["output_contains_any"] = list(a[1])
            check = a[1]
        elif isinstance(a, int):
            e["output_contains_any"] = forms_int(a)
            e["output_contains_any_token"] = True
            check = forms_int(a)
        else:
            e["output_contains"] = [a]
            if a.isdigit() and a.isascii():
                e["output_contains_token"] = True
            check = [a]
        assert any(c in lines[al - 1] for c in check), (cid, t["line"], check)
        dl = None
        if g1:
            assert al > 230, (cid, "answer line", al)
            assert t["decoy"], cid
            dl = find(lines, t["decoy"])
            assert dl < 150, (cid, "decoy line", dl)
        else:
            assert al < 60, (cid, "answer line", al)
            assert t["deep"], cid
            dl = find(lines, t["deep"])
            assert dl > 230, (cid, "deep line", dl)
        if t["excl"]:
            e["output_excludes"] = t["excl"]
        if tl == []:
            e["required_tools"] = ["read_file"]
        tl.append({"prompt": t["q"], "expect": e})
        facts.append({"line": t["line"], "decoy": t["decoy"] if g1 else t["deep"], "al": al, "dl": dl})
    multi = len(turns) > 1
    t0 = turns[0]["ans"]
    union = []
    for t in turns:
        a = t["ans"]
        for x in (list(a[1]) if isinstance(a, tuple) else forms_int(a) if isinstance(a, int) else []):
            if x not in union:
                union.append(x)
    if isinstance(t0, (tuple, int)):
        first = "print(json.dumps({\"expected_contains_any\": %s}, ensure_ascii=False))\n" % json.dumps(union, ensure_ascii=False)
    elif t0.isdigit():
        first = "print(json.dumps({\"expected_number\": float(%r)}))\n" % t0
    else:
        first = "print(json.dumps({\"expected_string\": %r}, ensure_ascii=False))\n" % t0
    ver = ("FACTS = json.loads(%r)\n"
           "ls = files[%r].split(\"\\n\")\n"
           "def at(sub):\n"
           "    h = [i + 1 for i, l in enumerate(ls) if sub in l]\n"
           "    assert len(h) == 1, (sub, h)\n"
           "    return h[0]\n"
           "for f in FACTS:\n"
           "    assert at(f[\"line\"]) == f[\"al\"] and at(f[\"decoy\"]) == f[\"dl\"], f\n"
           "    assert %s\n"
           % (json.dumps(facts, ensure_ascii=False), path,
              "f[\"al\"] > 230 and f[\"dl\"] < 150" if g1 else "f[\"al\"] < 60 and f[\"dl\"] > 230"))
    nt = "## Traps\n%s\n\n## Reference solution\n%s\n\n## Why the answer is unique\n%s\nFile has %d lines; answer line(s) %s; %s line(s) %s.\n" % (
        notes[0], notes[1], notes[2], n, [f["al"] for f in facts], "decoy" if g1 else "deep look-alike", [f["dl"] for f in facts])
    trap = "TR-TRUNC" if g1 else "TR-EARLYHIT"
    ce = {"max_calls": {"read_file": 4 if g1 else 1}}
    rc = ref_calls + (2 if multi and g1 else 0)
    level = "L1" if not multi or not g1 else "L2"
    zh = is_zh(" ".join(t["q"] for t in turns))
    num = cid.split("-")[1]
    BATCH.write_case(cid, desc=desc, task_type=TT.get(cid.split("-")[0], task_type) if task_type != "latest_version" else task_type, family="b23g-%s-%s" % (sub, num), level=level,
                     ref_calls=rc, files=files, turns=tl, verify=guard(files) + ver + first, notes=nt, traps=[trap],
                     decoys={trap: facts[0]["decoy"]}, axes=["OBS", "LNG"] + ([] if g1 else ["STP"]), answer_style="natural",
                     tool_policy=policy or (POL if g1 else POL0), extra_tags={"batch": "b23g", "subtype": sub}, case_expect=ce)
    META[cid] = {"sub": sub, "lang": "zh" if zh else "en", "turns": len(turns), "lines": n, "bytes": len(body.encode()),
                 "plen": sum(len(t["q"]) for t in turns) / len(turns), "al": [f["al"] for f in facts]}

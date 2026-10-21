"""b21k (v2.1 wave 3: workspace document tasks) shared writer."""
import hashlib
import inspect
import json
import os
import re
import sys
import textwrap

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from casegen import Batch  # noqa: E402

BATCH = Batch(salt="b21k", author="llm:claude-sonnet-b21k", version="v2.1", tool_catalog="agent-tool-v2.0")
EXTRA = {"batch": "b21k"}
META = {}
_V = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "workbank", "tag-vocab.json")))
TRAP_AXIS = {k: v.get("axis") for k, v in _V["traps"].items()}
TRAP_WORDS = {k: v.get("forbidden_words") or [] for k, v in _V["traps"].items()}
TOOLS = _V["tools"]
WEBOFF = ["web_search", "web_fetch"]
ROT_NEW = [("read_file", "write_file"), ("read_lines", "write_file"), ("bash",),
           ("read_file", "write_file", "append_file"), ("search_text", "read_file", "write_file")]
ROT_ASK = [("read_file",), ("read_lines",), ("bash",), ("search_text", "read_file"), ("read_file", "search_text")]

LINKCHK = '''
import posixpath, re, urllib.parse
def broken_links(files, doc):
    base = posixpath.dirname(doc)
    out = []
    text = files[doc]
    targets = re.findall(r"!?\\[[^\\]]*\\]\\(([^)\\s]+)\\)", text) + re.findall(r"(?m)^\\[[^\\]]+\\]:\\s*(\\S+)", text)
    for t in targets:
        if re.match(r"^([a-z]+:|#)", t):
            continue
        p = urllib.parse.unquote(t.split("#")[0].split("?")[0])
        if not p:
            continue
        full = posixpath.normpath(posixpath.join(base, p))
        if full not in files:
            out.append(t.split("#")[0])
    return out
'''


def is_zh(text):
    return len(re.findall(r"[一-鿿]", text)) >= 4


def level_for(n, ref_calls, n_files, multi):
    ok = []
    if n == 0 and ref_calls <= 3:
        ok.append("L0")
    if n == 1 and ref_calls <= 4:
        ok.append("L1")
    if n == 2 or (n == 1 and (n_files >= 3 or ref_calls >= 5)):
        ok.append("L2")
    if n >= 3 or (multi and n >= 1) or ref_calls >= 8:
        ok.append("L3")
    return ok


def mk(cid, *, sub, ttype, files, turns, rules=None, compute=None, ans=None, facts=None, links=None,
       traps=(), free=(), ref_calls=4, must=None, never=(), gist, steps, why, level=None):
    """turns: list of dict(p, inc, any, exc, req, excl_extra). rules: {path: list(contains)|str(equals)}.
    Files in fixture not named in rules are 'unchanged'. compute(files)->{path:text} reference output;
    facts: list of strings reference text is built from; ans(files)->str for answer cases;
    links=(doc, [broken...]) for link-check answer cases."""
    k = int(cid[-2:]) % 5
    if must is None:
        must = ROT_NEW[k] if rules else ROT_ASK[k]
    prompts = [t["p"] for t in turns]
    for p in prompts:
        low = re.sub(r"\s+", " ", p.lower())
        for t in TOOLS:
            assert t not in low, (cid, t)
        for trap in traps:
            for w in TRAP_WORDS[trap]:
                assert w.lower() not in low, (cid, trap, w)
    efiles = {}
    if rules is not None:
        for path in files:
            if path not in rules:
                efiles[path] = {"unchanged": True}
        for path, r in rules.items():
            efiles[path] = {"equals": r} if isinstance(r, str) else {"contains": list(r)}
            par = os.path.dirname(path)
            assert not par or any(f.startswith(par + "/") for f in files), (cid, path)
    tturns = []
    for t in turns:
        e = {}
        if t.get("inc"):
            e["output_contains"] = list(t["inc"])
            if any(re.fullmatch(r"[A-Za-z0-9._/\-]+", x) for x in t["inc"]):
                e["output_contains_token"] = True
        if t.get("any"):
            e["output_contains_any"] = list(t["any"])
        e["output_excludes"] = ["UNKNOWN"] + list(t.get("exc", []))
        if t.get("req"):
            e["required_tools"] = list(t["req"])
        if t.get("max"):
            e["max_output_chars"] = t["max"]
        tturns.append({"prompt": t["p"], "expect": e})
        if t.get("review"):
            tturns[-1]["review_before"] = t["review"]
    multi = len(turns) > 1
    lv = level_for(len(traps), ref_calls, len(files), multi)
    if level:
        assert level in lv, (cid, level, lv)
    else:
        level = [x for x in lv if x != "L0"][0] if len(lv) > 1 else lv[0]
    axes = list(dict.fromkeys(["OBS"] + [TRAP_AXIS[x] for x in traps if TRAP_AXIS[x] != "OBS"]))
    digest = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    head = ("import hashlib, json\ncase = json.load(open(\"case.json\"))\n"
            "_pin = hashlib.sha256(json.dumps(case[\"files\"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()\n"
            "assert _pin == %r, \"fixture changed\"\nfiles = case[\"files\"]\n" % digest)
    if compute is not None or facts is not None:
        if facts is not None:
            body = ("FACTS = json.loads(%r)\n"
                    "corpus = \"\".join(files.values()) + \"\".join(t[\"prompt\"] for t in case[\"turns\"])\n"
                    "FREE = json.loads(%r)\n"
                    "assert all(f in corpus for f in FACTS if f not in FREE), [f for f in FACTS if f not in corpus and f not in FREE]\n"
                    "FINAL = {p: \"\\n\".join(FACTS) for p, r in case[\"expect\"][\"files\"].items() if \"contains\" in r}\n"
                    % (json.dumps(facts, ensure_ascii=False), json.dumps(list(free), ensure_ascii=False)))
        else:
            body = textwrap.dedent(inspect.getsource(compute)) + "\nFINAL = compute(dict(files))\n"
        body += ("for path, rule in case[\"expect\"][\"files\"].items():\n"
                 "    if \"equals\" in rule:\n        assert FINAL[path] == rule[\"equals\"], path\n"
                 "    elif \"contains\" in rule:\n        assert all(s in FINAL[path] for s in rule[\"contains\"]), path\n"
                 "print(json.dumps({\"files\": {k: v for k, v in FINAL.items() if k in case[\"expect\"][\"files\"] "
                 "and \"unchanged\" not in case[\"expect\"][\"files\"][k]}}, ensure_ascii=False))\n")
        verify = head + body
    elif links is not None:
        doc, brk = links
        docs = doc if isinstance(doc, list) else [doc]
        verify = (head + LINKCHK + "got = [b for d in %r for b in broken_links(files, d)]\nWANT = json.loads(%r)\n"
                  "assert sorted(got) == sorted(WANT), (got, WANT)\n"
                  "inc = [x for t in case[\"turns\"] for x in t[\"expect\"].get(\"output_contains\", [])]\n"
                  "inc += [x for r in case.get(\"expect\", {}).get(\"files\", {}).values() for x in r.get(\"contains\", [])]\n"
                  "assert all(w in inc for w in WANT), WANT\n"
                  "first = case[\"turns\"][0][\"expect\"].get(\"output_contains\", [WANT[0]])[0]\n"
                  "assert not first.isdigit() or first == str(len(WANT)), first\n"
                  "print(json.dumps({\"expected_string\": first}, ensure_ascii=False))\n" % (docs, json.dumps(brk, ensure_ascii=False)))
    else:
        verify = head + textwrap.dedent(inspect.getsource(ans)) + (
            "\nV = answer(files)\ninc = [x for t in case[\"turns\"] for x in t[\"expect\"].get(\"output_contains\", [])]\n"
            "assert V in inc, (V, inc)\nprint(json.dumps({\"expected_string\": V}, ensure_ascii=False))\n")
    nt = "## Traps\n%s\n\n## Reference solution\n%s\n\n## Why the answer is unique\n%s\nExpected: %s\n" % (
        ", ".join(traps) if traps else "none", steps, why,
        "; ".join(x for t in turns for x in t.get("inc", [])) or "see case.json expect.files")
    ce = {"files": efiles} if rules is not None else None
    fam = "b21k-%s-%s" % (sub, cid.split("-")[1][-2:])
    BATCH.write_case(cid, desc=gist, task_type=ttype, family=fam, level=level, ref_calls=ref_calls, files=files,
                     turns=tturns, verify=verify, notes=nt, traps=list(traps), decoys={x: (None if rules is not None else "0") for x in traps},
                     axes=axes, case_expect=ce, answer_style="natural",
                     tool_policy={"must_offer": list(must), "never_offer": list(never)}, extra_tags=EXTRA)
    META[cid] = {"sub": sub, "zh": is_zh(" ".join(prompts)), "turns": len(turns), "level": level,
                 "policy": "+".join(must), "never": bool(never)}

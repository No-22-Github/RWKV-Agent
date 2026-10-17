"""b21o (v2.1 wave 3: special tools -- weather / datetime / calculator / data_query / local-file combos, ids 33601-33670).

A case: fixture files + weather fixture + turns + compute(files, wx) -> (final_files, answers).
compute is the single source of truth: it is embedded in verify.py and re-run against the fixture;
expect.files and every turn's answer expectations are derived from it.
answers: one list per turn of ("num", v) | ("all", [..]) | ("any", [..]).
"""
import hashlib
import inspect
import json
import os
import random
import re
import sys
import textwrap

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from casegen import Batch, weather  # noqa: E402,F401

BATCH = Batch(salt="b21o", author="llm:claude-sonnet-b21o", version="v2.1", tool_catalog="work-v2")
EXTRA = {"batch": "b21o"}
META = {}
_VOCAB = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "workbank", "tag-vocab.json")))
TRAP_AXIS = {k: v.get("axis") for k, v in _VOCAB["traps"].items()}
TRAP_WORDS = {k: v.get("forbidden_words") or [] for k, v in _VOCAB["traps"].items()}
TOOLS = _VOCAB["tools"]
WEBX = ["web_search", "web_fetch"]


def is_zh(text):
    return len(re.findall(r"[一-鿿]", text)) >= 4


def allowed(n, rc, nfiles, multi):
    v = set()
    if n == 0 and rc <= 3:
        v.add("L0")
    if n == 1 and rc <= 4:
        v.add("L1")
    if n == 2 or (n == 1 and (nfiles >= 3 or rc >= 5)):
        v.add("L2")
    if n >= 3 or (multi and n >= 1) or rc >= 8:
        v.add("L3")
    return v


def L(*rows):
    return "".join(r + "\n" for r in rows)


def rng(seed):
    return random.Random("b21o-%s" % seed)


def money(x):
    """spellings of a money value with <=2 decimals (plain / thousands)."""
    x = round(x, 2)
    a = "%.2f" % x
    out = [a, a.rstrip("0").rstrip(".")]
    if abs(x) >= 1000:
        out += ["{:,.2f}".format(x), "{:,.2f}".format(x).rstrip("0").rstrip(".")]
    return list(dict.fromkeys(out))


def mk(cid, *, sub, task="special_tool", desc, files=None, wx=None, turns, compute, must, never=(), traps=(),
       decoys=None, rc=2, notes="", alts=None, fam=None):
    """turns: list of dicts {p, req, forb, ex, review, tol, tools}."""
    files = dict(files or {})
    wx = list(wx or [])
    final, answers = compute(json.loads(json.dumps(files)), json.loads(json.dumps(wx)))
    assert len(answers) == len(turns), (cid, len(answers), len(turns))
    src = textwrap.dedent(inspect.getsource(compute))
    ns = {}
    exec(src, ns)
    f2, a2 = ns["compute"](json.loads(json.dumps(files)), json.loads(json.dumps(wx)))
    assert f2 == final and json.dumps(a2) == json.dumps(answers), cid
    for t in turns:
        low = re.sub(r"\s+", " ", t["p"].lower())
        for tn in TOOLS:
            assert tn not in low, (cid, tn)
        for trap in traps:
            for w in TRAP_WORDS[trap]:
                assert w.lower() not in low, (cid, trap, w)
        assert not re.search(r"测试|判据|verify|benchmark", low), (cid, t["p"])
    efiles = {}
    for path in files:
        if path not in final:
            efiles[path] = {"unchanged": True}
    for path, text in final.items():
        efiles[path] = {"contains": list(text)} if isinstance(text, list) else {"equals": text}
    tturns = []
    for t, ans in zip(turns, answers):
        e = {}
        for kind, val in ans:
            if kind == "num":
                e["expected_number"] = float(val)
                e["expected_number_in_text"] = True
                e["tolerance"] = t.get("tol", 0.01)
            elif kind == "all":
                e["output_contains"] = list(val)
                if any(re.fullmatch(r"[\d:.\-/]{1,10}", x) for x in val):
                    e["output_contains_token"] = True
            elif kind == "any":
                e["output_contains_any"] = list(val)
                if all(re.fullmatch(r"[\d,.]+", x) for x in val):
                    e["output_contains_any_token"] = True
        if t.get("req"):
            e["required_tools"] = list(t["req"])
        if t.get("forb"):
            e["forbidden_tools"] = list(t["forb"])
        if t.get("tools") is not None:
            e["tools"] = t["tools"]
        if t.get("ex"):
            e["output_excludes"] = list(t["ex"])
        if not e:
            e["output_excludes"] = ["UNKNOWN"]
        d = {"prompt": t["p"], "expect": e}
        if t.get("review"):
            d["review_before"] = t["review"]
        tturns.append(d)
    multi = len(turns) > 1
    ok = sorted(x for x in allowed(len(traps), rc, len(files), multi) if x != "L0")
    level = ok[0] if ok else "L0"
    if not traps and rc <= 3 and not multi:
        level = "L0"
    # verify: pin fixtures, recompute, print one recognised shape
    digest = hashlib.sha256(json.dumps({"f": files, "w": wx}, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    verify = ("import hashlib, json\n"
              "case = json.load(open(\"case.json\"))\n"
              "_pin = hashlib.sha256(json.dumps({\"f\": case[\"files\"], \"w\": case.get(\"weather_fixture\", [])}, ensure_ascii=False, sort_keys=True).encode()).hexdigest()\n"
              "assert _pin == %r, \"fixture changed\"\n" % digest + src + "\n"
              "FINAL, ANS = compute(dict(case[\"files\"]), case.get(\"weather_fixture\", []))\n"
              "for path, rule in case.get(\"expect\", {}).get(\"files\", {}).items():\n"
              "    if \"equals\" in rule:\n"
              "        assert FINAL[path] == rule[\"equals\"], path\n"
              "    elif \"contains\" in rule:\n"
              "        assert FINAL[path] == rule[\"contains\"], path\n"
              "    elif rule.get(\"unchanged\"):\n"
              "        assert path in case[\"files\"] and path not in FINAL, path\n"
              "flat = [x for a in ANS for x in a]\n"
              "nums = [v for k, v in flat if k == \"num\"]\n"
              "alls = [v for k, v in flat if k == \"all\"]\n"
              "anys = [x for k, v in flat if k == \"any\" for x in v]\n"
              "for turn, a in zip(case[\"turns\"], ANS):\n"
              "    e = turn[\"expect\"]\n"
              "    for k, v in a:\n"
              "        if k == \"num\":\n"
              "            assert abs(e[\"expected_number\"] - v) < 1e-9\n"
              "        elif k == \"all\":\n"
              "            assert e[\"output_contains\"] == v\n"
              "        else:\n"
              "            assert e[\"output_contains_any\"] == v\n"
              "if FINAL:\n"
              "    print(json.dumps({\"files\": {k: (\"\\n\".join(v) if isinstance(v, list) else v) for k, v in FINAL.items()}}, ensure_ascii=False))\n"
              "elif nums:\n"
              "    print(json.dumps({\"expected_number\": float(nums[0])}))\n"
              "elif anys:\n"
              "    print(json.dumps({\"expected_contains_any\": anys}, ensure_ascii=False))\n"
              "else:\n"
              "    print(json.dumps({\"expected_string\": alls[0][0]}, ensure_ascii=False))\n")
    # when several turns carry output_contains_any, the verify union must equal the case-level union
    pol = {"must_offer": list(must)}
    if never:
        pol["never_offer"] = list(never)
    axes = list(dict.fromkeys(["OBS"] + [TRAP_AXIS[t] for t in traps]))
    first = turns[0]["p"]
    alts = alts or []
    assert len(alts) == 5, (cid, "need 5 phrasings")
    exp_txt = "; ".join(json.dumps(a, ensure_ascii=False) for turn in answers for a in turn)
    nums = [str(v) for turn in answers for k, v in turn if k == "num"]
    nt = ("## Traps\n%s\n\n## Reference solution\n%s\n\n## Why the answer is unique\nRecomputed from the fixture / fixed clock "
          "(2026-09-16 10:00 Asia/Shanghai). Expected: %s %s\n\n## Five alternative phrasings of the task\n%s" % (
              ", ".join(traps) if traps else "none", notes, exp_txt, " ".join(nums),
              "".join("%d. %s\n" % (i + 1, a) for i, a in enumerate(alts))))
    dec = dict(decoys or {})
    for t in traps:
        dec.setdefault(t, "n/a")
    fam = fam or "b21o-%s-%s" % (sub, cid.split("-")[1][-2:])
    BATCH.write_case(cid, desc=desc, task_type=task, family=fam, level=level, ref_calls=rc, files=files,
                     turns=tturns, verify=verify, notes=nt, traps=list(traps), decoys=dec, axes=axes,
                     case_expect={"files": efiles} if efiles else None, answer_style="natural",
                     tool_policy=pol, extra_tags=EXTRA, weather_fixture=wx or None)
    META[cid] = {"sub": sub, "zh": is_zh(" ".join(t["p"] for t in turns)), "turns": len(turns), "level": level,
                 "policy": "+".join(must)}

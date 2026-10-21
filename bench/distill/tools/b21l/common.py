"""b21l (v2.1 wave 3: hybrid multi-tool tasks, ids 33301-33380) shared writer.

A case is: fixture files + web_fixture + turns + compute(files, web) -> (final_files, answers).
compute is the single source of truth: it is embedded in verify.py, re-run against the
fixture, and both the expect.files and every turn's answer strings are derived from it.
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
from casegen import Batch  # noqa: E402

BATCH = Batch(salt="b21l", author="llm:claude-sonnet-b21l", version="v2.1", tool_catalog="agent-tool-v2.0")
EXTRA = {"batch": "b21l"}
META = {}
_VOCAB = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "workbank", "tag-vocab.json")))
TRAP_AXIS = {k: v.get("axis") for k, v in _VOCAB["traps"].items()}
TRAP_WORDS = {k: v.get("forbidden_words") or [] for k, v in _VOCAB["traps"].items()}
TOOLS = _VOCAB["tools"]
TASK = {"web_edit": "web_then_edit", "write": "tool_then_write", "calc": "web_then_calc",
        "comp": "compound_request", "multi": "multi_turn"}

WEB = ["web_search", "web_fetch"]


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


def nv(n):
    """integer spellings: plain and thousands-separated."""
    s = [str(n)]
    if abs(n) >= 1000:
        s.append("{:,}".format(n))
    return s


def nv2(x):
    """money-ish spellings of a value with <=2 decimals."""
    x = round(x, 2)
    if abs(x - round(x)) < 1e-9:
        return nv(int(round(x))) + ["%d.00" % round(x)] + (["{:,}.00".format(int(round(x)))] if x >= 1000 else [])
    a = "%.2f" % x
    b = ("%.2f" % x).rstrip("0")
    out = [a, b]
    if x >= 1000:
        out += ["{:,.2f}".format(x), "{:,.2f}".format(x).rstrip("0")]
    return list(dict.fromkeys(out))


def mk(cid, *, sub, desc, files, turns, compute, must, never=(), web=(), traps=(), rc=4, loose=(), fam=None,
       notes="", also=None, weather=None):
    """turns: list of dicts {p, any(bool), ex(list), req(list), review(str)}; answers come from compute."""
    web = list(web)
    final, answers = compute(dict(files), json.loads(json.dumps(web)))
    assert len(answers) == len(turns), (cid, len(answers), len(turns))
    # isolation: the embedded source must reproduce the same result in a clean namespace
    src = textwrap.dedent(inspect.getsource(compute))
    ns = {}
    exec(src, ns)
    f2, a2 = ns["compute"](dict(files), json.loads(json.dumps(web)))
    assert f2 == final and a2 == answers, cid
    for p in [t["p"] for t in turns]:
        low = re.sub(r"\s+", " ", p.lower())
        for t in TOOLS:
            assert t not in low, (cid, t)
        for trap in traps:
            for w in TRAP_WORDS[trap]:
                assert w.lower() not in low, (cid, trap, w)
        assert not re.search(r"测试|判据|verify|benchmark", low), (cid, p)
    efiles = {}
    for path in files:
        if path not in final:
            efiles[path] = {"unchanged": True}
    for path, text in final.items():
        if path in loose:
            efiles[path] = {"contains": [l for l in text.split("\n") if l.strip()]}
        else:
            efiles[path] = {"equals": text}
    if also:
        efiles.update(also)
    tturns = []
    for t, ans in zip(turns, answers):
        e = {}
        if t.get("any"):
            e["output_contains_any"] = list(ans)
            if all(re.fullmatch(r"[\d,.]+", x) for x in ans):
                e["output_contains_any_token"] = True
        elif ans:
            e["output_contains"] = list(ans)
            if any(re.fullmatch(r"\d{1,3}", x) for x in ans):
                e["output_contains_token"] = True
        if t.get("ex"):
            e["output_excludes"] = list(t["ex"])
            for x in t["ex"]:
                assert not any(x in a for a in ans), (cid, x)
        if t.get("req"):
            e["required_tools"] = list(t["req"])
        if t.get("tools") is not None:
            e["tools"] = t["tools"]
        if not e:
            e["output_excludes"] = ["UNKNOWN"]
        d = {"prompt": t["p"], "expect": e}
        if t.get("review"):
            d["review_before"] = t["review"]
        tturns.append(d)
    multi = len(turns) > 1
    ok = sorted(x for x in allowed(len(traps), rc, len(files), multi) if x != "L0")
    level = ok[0] if ok else "L2"
    digest = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    verify = ("import hashlib, json\n"
              "case = json.load(open(\"case.json\"))\n"
              "_pin = hashlib.sha256(json.dumps(case[\"files\"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()\n"
              "assert _pin == %r, \"fixture changed\"\n" % digest + src + "\n"
              "FINAL, ANS = compute(dict(case[\"files\"]), case[\"web_fixture\"])\n"
              "for path, rule in case[\"expect\"][\"files\"].items():\n"
              "    if \"equals\" in rule:\n"
              "        assert FINAL[path] == rule[\"equals\"], path\n"
              "    elif \"contains\" in rule:\n"
              "        assert all(s in FINAL[path] for s in rule[\"contains\"]), path\n"
              "    elif rule.get(\"unchanged\"):\n"
              "        assert path in case[\"files\"] and path not in FINAL, path\n"
              "for turn, a in zip(case[\"turns\"], ANS):\n"
              "    e = turn[\"expect\"]\n"
              "    assert set(a) <= set(e.get(\"output_contains\", [])) | set(e.get(\"output_contains_any\", [])), a\n"
              "print(json.dumps({\"files\": {k: v for k, v in FINAL.items() if k in case[\"expect\"][\"files\"]}, \"answers\": ANS}, ensure_ascii=False))\n")
    pol = {"must_offer": list(must), "never_offer": list(never)}
    axes = ["OBS", "CHN"] + [TRAP_AXIS[t] for t in traps]
    axes = list(dict.fromkeys(axes))
    alts = [desc, "Same job, other words: " + desc, "Please " + desc, desc + " (final state matters)", "Do this for me: " + desc]
    nt = ("## Traps\n%s\n\n## Reference solution\n%s\n\n## Why the answer is unique\nThe expected values are recomputed by verify.py from the fixture and web_fixture.\n\n## Five alternative phrasings of the task\n%s" % (
        ", ".join(traps) if traps else "none", notes, "".join("%d. %s\n" % (i + 1, a) for i, a in enumerate(alts))))
    fam = fam or "b21l-%s-%s" % (sub, cid.split("-")[1][-2:])
    BATCH.write_case(cid, desc=desc, task_type=TASK[sub], family=fam, level=level, ref_calls=rc, files=files,
                     turns=tturns, verify=verify, notes=nt, traps=list(traps), decoys={t: None for t in traps},
                     axes=axes, case_expect={"files": efiles}, answer_style="natural", tool_policy=pol,
                     extra_tags=EXTRA, web=web, weather_fixture=weather)
    META[cid] = {"sub": sub, "zh": is_zh(" ".join(t["p"] for t in turns)), "turns": len(turns), "level": level,
                 "policy": "+".join(must), "web": bool(web)}


def page(q, url, title, snippet, content=None, pub=None, err=None, match=None):
    e = {"query_match": q, "url_match": match or url.split("://", 1)[1].rstrip("/"), "url": url, "title": title, "snippet": snippet}
    if content is not None:
        e["content"] = content
    if pub:
        e["published_at"] = pub
    if err:
        e["error"] = err
    return e


def L(*rows):
    return "".join(r + "\n" for r in rows)


def rng(seed):
    return random.Random("b21l-%s" % seed)

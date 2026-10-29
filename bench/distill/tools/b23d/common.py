"""b23d (v2.3: 3-4 user-turn conversations, ids 35201-35260) shared writer.

A case is: fixture files + turns + declarative edits. The final file state is derived
from `edits` (path, old, new: old must occur exactly once) and `adds` (path, text appended
to an existing file or creating a new one); verify.py re-applies them to the fixture.
Every expected output string in `inc` must be visible in the fixture, the final files or a prompt.
"""
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from casegen import Batch  # noqa: E402

BATCH = Batch(salt="b23d", author="llm:claude-sonnet-b23d", version="v2.3", tool_catalog="agent-tool-v3.2")
META = {}
TOOLS = ["list_files", "read_file", "search_text", "write_file", "replace_lines", "append_file", "calculator",
         "data_query", "datetime", "web_search", "web_fetch", "get_weather", "bash"]
READ = ["list_files", "read_file", "search_text"]
WRITE = ["write_file", "replace_lines", "append_file"]
AXIS = {"TR-CLAIM": "VER", "TR-MULTISRC": "CON", "TR-DECOY": "OBS", "TR-SUPERSEDE": "VER", "TR-NEARNAME": "OBS", "TR-AMBIG": "DEC"}
TASK = {"multi": "multi_turn", "undo": "undo_change", "write": "tool_then_write", "comp": "compound_request"}


def is_zh(text):
    return len(re.findall(r"[一-鿿]", text)) >= 4


def L(*rows):
    return "".join(r + "\n" for r in rows)


def T(p, inc=(), any=(), exc=(), req=(), forb=(), review=None, tools=None):
    return dict(p=p, inc=list(inc), any=list(any), exc=list(exc), req=list(req), forb=list(forb), review=review, tools=tools)


def apply(files, edits, adds):
    out = {}
    for path, old, new in edits:
        cur = out.get(path, files[path])
        assert cur.count(old) == 1, (path, old)
        out[path] = cur.replace(old, new)
    for path, text in adds:
        out[path] = out.get(path, files.get(path, "")) + text
    return out


def level(n_traps, rc, n_files):
    return "L3"  # multi-turn with a declared trap allows L3 (lint "level" rule)


def mk(cid, *, sub, tt, trap, desc, files, turns, must, edits=(), adds=(), writes=None, loose=(), exact=(), rc, max_calls=None, notes="", dep=None, vals=()):
    n = len(turns)
    assert n in (3, 4), cid
    assert rc <= 12 and rc >= n - 1, (cid, rc)
    edits, adds = [tuple(e) for e in edits], [tuple(a) for a in adds]
    final = apply(files, edits, adds)
    prompts = [t["p"] for t in turns]
    pool = " ".join(files.values()) + " " + " ".join(files.keys()) + " " + " ".join(final.values()) + " " + " ".join(prompts) + " " + " ".join(vals)
    for p in prompts:
        low = p.lower()
        for t in TOOLS:
            assert t not in low, (cid, t)
        assert not re.search(r"测试|判据|verify|benchmark", low), (cid, p)
        assert not re.search(r"\.example\b", p), cid
    writes = writes or {}
    efiles = {}
    for path in files:
        if path not in final:
            efiles[path] = {"unchanged": True}
    for path, text in final.items():
        if path in writes:
            continue
        if path in loose or (path not in files and path not in exact):
            efiles[path] = {"contains": [l for l in text.split("\n") if l.strip()]}
        else:
            efiles[path] = {"equals": text}
    for path, subs in writes.items():
        efiles[path] = {"contains": list(subs)}
    tt_ = []
    for t in turns:
        e = {}
        if t["inc"]:
            for x in t["inc"]:
                assert x in pool or (x.isdigit() and len(x) <= 3), (cid, x)
            e["output_contains"] = t["inc"]
            if any(re.fullmatch(r"[\d.]{1,3}", x) or (x.isascii() and re.fullmatch(r"[A-Za-z0-9_.-]{1,3}", x)) for x in t["inc"]):
                e["output_contains_token"] = True
        if t["any"]:
            e["output_contains_any"] = t["any"]
        if t["exc"]:
            e["output_excludes"] = t["exc"]
            for x in t["exc"]:
                assert x not in " ".join(t["inc"]), (cid, x)
        if t["req"]:
            e["required_tools"] = t["req"]
        if t["forb"]:
            e["forbidden_tools"] = t["forb"]
        if t["tools"] is not None:
            e["tools"] = t["tools"]
        if not e:
            e["output_excludes"] = ["UNKNOWN"]
        d = {"prompt": t["p"], "expect": e}
        if t["review"]:
            d["review_before"] = t["review"]
        tt_.append(d)
    # the last turn must rest on turn-1 facts: at least one last-turn string has to be absent from the final files and
    # present in the original fixture or in turn 1's prompt (i.e. it was only knowable from the first turn)
    last = turns[-1]["inc"] + turns[-1]["any"]
    first_pool = " ".join(files.values()) + " " + " ".join(files) + " " + prompts[0]
    assert dep or any(x in first_pool for x in turns[-1]["inc"]), (cid, "last turn does not use turn-1 facts")
    digest = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    verify = ("import hashlib, json\n"
              "case = json.load(open(\"case.json\"))\n"
              "_pin = hashlib.sha256(json.dumps(case[\"files\"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()\n"
              "assert _pin == %r, \"fixture changed\"\n" % digest +
              "EDITS = %s\nADDS = %s\nVALS = %s\nWRITES = %s\n" % (json.dumps(edits, ensure_ascii=False), json.dumps(adds, ensure_ascii=False), json.dumps(list(vals), ensure_ascii=False), json.dumps(writes, ensure_ascii=False)) +
              "files = dict(case[\"files\"])\nfinal = {}\n"
              "for path, old, new in EDITS:\n"
              "    cur = final.get(path, files[path])\n"
              "    assert cur.count(old) == 1, (path, old)\n"
              "    final[path] = cur.replace(old, new)\n"
              "for path, text in ADDS:\n"
              "    final[path] = final.get(path, files.get(path, \"\")) + text\n"
              "for path, subs in WRITES.items():\n"
              "    final[path] = \"\\n\".join(subs)\n"
              "pool0 = \" \".join(files.values()) + \" \" + \" \".join(t[\"prompt\"] for t in case[\"turns\"])\n"
              "for path, rule in case[\"expect\"][\"files\"].items():\n"
              "    if \"equals\" in rule:\n"
              "        assert final[path] == rule[\"equals\"], path\n"
              "    elif \"contains\" in rule:\n"
              "        if path in final:\n"
              "            assert all(s in final[path] for s in rule[\"contains\"]), path\n"
              "        else:\n"
              "            assert path not in files, path\n"
              "    elif rule.get(\"unchanged\"):\n"
              "        assert path in files and path not in final, path\n"
              "pool = \" \".join(files.values()) + \" \" + \" \".join(files) + \" \" + \" \".join(final.values()) + \" \" + \" \".join(t[\"prompt\"] for t in case[\"turns\"]) + \" \" + \" \".join(VALS)\n"
              "for turn in case[\"turns\"]:\n"
              "    for s in turn[\"expect\"].get(\"output_contains\", []):\n"
              "        assert s in pool or (s.isdigit() and len(s) <= 3), s\n"
              "print(json.dumps({\"files\": final, \"answers\": [t[\"expect\"].get(\"output_contains\", []) for t in case[\"turns\"]]}, ensure_ascii=False))\n")
    lvl = level(1, rc, len(files))
    alts = [prompts[0], "Quick one: " + prompts[0], prompts[0] + " (short answer is fine)", "Hi, " + prompts[0], "Next task: " + prompts[0]]
    ref = (notes or "see turns") + (("\nLast-turn dependency: " + dep) if dep else "")
    nt = ("## Traps\n- %s\n\n## Reference solution\n%s\n\n## Why the answer is unique\nExpected strings are visible in the fixture or in the final files that verify.py recomputes from the declared edits; "
          "the last turn needs a fact only turn 1 revealed.\n\n## Five alternative phrasings of the task\n%s" % (
              trap, ref, "".join("%d. %s\n" % (i + 1, a) for i, a in enumerate(alts))))
    pol = {"must_offer": list(must)}
    ce = {"files": efiles}
    if max_calls:
        ce["max_calls"] = max_calls
    BATCH.write_case(cid, desc=desc, task_type=TASK[tt], family="b23d-%s-%s" % (sub, cid.split("-")[1]),
                     level=lvl, ref_calls=rc, files=files, turns=tt_, verify=verify, notes=nt, traps=[trap],
                     decoys={trap: None}, axes=list(dict.fromkeys(["OBS", "CHN", AXIS[trap]])), case_expect=ce,
                     answer_style="natural", tool_policy=pol, extra_tags={"batch": "b23d", "subtype": sub})
    META[cid] = {"sub": sub, "zh": is_zh(" ".join(prompts)), "turns": n, "level": lvl, "chars": len(prompts[0]), "tt": tt, "rc": rc}

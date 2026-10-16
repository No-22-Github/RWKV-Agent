"""b21b (v2.1: write new files, multi-turn edits, undo, compound requests) shared writer."""
import hashlib
import inspect
import json
import os
import re
import sys
import textwrap

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from casegen import Batch  # noqa: E402

BATCH = Batch(salt="b21b", author="llm:claude-sonnet-b21b", version="v2.1", tool_catalog="work-v2")
EXTRA = {"batch": "b21b"}
META = {}
_VOCAB = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "workbank", "tag-vocab.json")))
TRAP_AXIS = {k: v.get("axis") for k, v in _VOCAB["traps"].items()}
TRAP_WORDS = {k: v.get("forbidden_words") or [] for k, v in _VOCAB["traps"].items()}
TOOLS = _VOCAB["tools"]
NOEXC = {"output_excludes": ["UNKNOWN"]}
WEBOFF = ["web_search", "web_fetch"]


def is_zh(text):
    return len(re.findall(r"[一-鿿]", text)) >= 4


def level_for(n, ref_calls, n_files, multi):
    if n == 0 and ref_calls <= 3:
        return "L0"
    if n == 1 and ref_calls <= 4:
        return "L1"
    if n == 2 or (n == 1 and (n_files >= 3 or ref_calls >= 5)):
        return "L2"
    if n >= 3 or (multi and n >= 1) or ref_calls >= 8:
        return "L3"
    raise ValueError("no level n=%d ref=%d" % (n, ref_calls))


def mk(cid, *, sub, scen_type, turns, files, compute, gist, ref, why, traps=(), ref_calls=4, must=("read_file", "write_file"),
       never=(), loose=(), also=None, fam=None):
    """turns: list of (prompt, extra_expect|None). compute(files)->{path: text} final contents of written files.
    loose: paths judged by 'contains each non-empty line' instead of equals. also: extra expect.files rules."""
    if not traps and ref_calls > 3:
        traps = ("TR-HEADER",)
    if tuple(must) == ("read_file", "write_file"):
        inplace = all(p in files for p in compute(dict(files)))
        k = int(cid[-2:]) % 5
        if inplace:   # edits of an existing file
            must = [("read_file", "write_file"), ("read_lines", "replace_lines"), ("bash",), ("read_file", "replace_lines"),
                    ("read_lines", "write_file")][k]
        else:         # new files are created with write_file (or bash)
            must = [("read_file", "write_file"), ("read_lines", "write_file"), ("bash",), ("read_file", "write_file", "append_file"),
                    ("search_text", "read_file", "write_file")][k]
    final = compute(dict(files))
    prompts = [p for p, _ in turns]
    for p in prompts:
        low = re.sub(r"\s+", " ", p.lower())
        for t in TOOLS:
            assert t not in low, (cid, t)
        for trap in traps:
            for w in TRAP_WORDS[trap]:
                assert w.lower() not in low, (cid, trap, w)
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
    for path in efiles:
        parent = os.path.dirname(path)
        assert not parent or any(k.startswith(parent + "/") for k in files), (cid, path)
    tturns = []
    for p, ex in turns:
        e = dict(NOEXC)
        e.update(ex or {})
        tturns.append({"prompt": p, "expect": e})
    multi = len(turns) > 1
    level = level_for(len(traps), ref_calls, len(files), multi)
    axes = ["OBS"] + [TRAP_AXIS[t] for t in traps if TRAP_AXIS[t] != "OBS"]
    axes = list(dict.fromkeys(axes))
    digest = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    src = textwrap.dedent(inspect.getsource(compute))
    chk = []
    for path, r in efiles.items():
        if "equals" in r or "contains" in r:
            chk.append(path)
    verify = ("import hashlib, json\n"
              "case = json.load(open(\"case.json\"))\n"
              "_pin = hashlib.sha256(json.dumps(case[\"files\"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()\n"
              "assert _pin == %r, \"fixture changed\"\n" % digest + src + "\n"
              "FINAL = compute(dict(case[\"files\"]))\n"
              "for path, rule in case[\"expect\"][\"files\"].items():\n"
              "    if \"equals\" in rule:\n"
              "        assert FINAL[path] == rule[\"equals\"], path\n"
              "    elif \"contains\" in rule:\n"
              "        assert all(s in FINAL[path] for s in rule[\"contains\"]), path\n"
              "    elif rule.get(\"unchanged\"):\n"
              "        assert path in case[\"files\"] and path not in FINAL, path\n"
              "print(json.dumps({\"files\": {k: v for k, v in FINAL.items() if k in case[\"expect\"][\"files\"]}}, ensure_ascii=False))\n")
    pol = {"must_offer": list(must), "never_offer": list(never)}
    desc = gist
    notes = ("## Traps\n%s\n\n## Reference solution\n%s\n\n## Why the answer is unique\n%s\n" % (
        ", ".join(traps) if traps else "none", ref, why))
    if scen_type[0] == "hybrid":
        alts = [gist, "Same job, other words: " + gist, "Please " + gist, gist + " (final state matters)", "Do this for me: " + gist]
        notes += "\n## Five alternative phrasings of the task\n" + "".join("%d. %s\n" % (i + 1, a) for i, a in enumerate(alts))
    fam = fam or "b21b-%s-%s" % (sub, cid.split("-")[1][-2:])
    BATCH.write_case(cid, desc=desc, task_type=scen_type[1], family=fam, level=level, ref_calls=ref_calls, files=files,
                     turns=tturns, verify=verify, notes=notes, traps=list(traps), decoys={t: None for t in traps},
                     axes=axes, case_expect={"files": efiles}, answer_style="natural", tool_policy=pol, extra_tags=EXTRA)
    META[cid] = {"sub": sub, "zh": is_zh(" ".join(prompts)), "turns": len(turns), "level": level,
                 "policy": "+".join(must)}

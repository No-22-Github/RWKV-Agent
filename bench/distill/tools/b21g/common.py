"""b21g (v2.1: JSON/JSONL and many-file aggregation with bash) shared framework.

A case = fixture files + a solve(files) function. solve is written as plain
stdlib Python, run here to get the truth and embedded verbatim in verify.py
(which re-runs it on case.json's fixture). A bash reference is replayed in the
just-bash sidecar and must print the same answer.
"""
import base64
import hashlib
import inspect
import json
import os
import re
import shutil
import sys
import tempfile
import textwrap
from random import Random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from casegen import Batch, Sidecar  # noqa: E402,F401

BATCH = Batch(salt="b21g", author="llm:claude-sonnet-b21g", version="v2.1", tool_catalog="work-v2")
EXTRA = {"batch": "b21g"}
META = {}
REFS = {}
_VOCAB = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "workbank", "tag-vocab.json")))
TRAP_AXIS = {k: v.get("axis") for k, v in _VOCAB["traps"].items()}
NOWEB = ["web_search", "web_fetch"]
READS = ["read_file", "list_files", "search_text"]


B = []


def reg(f):
    """Register a case builder f(attempt); an AssertionError (data-dependent
    uniqueness check) retries with the next seed."""
    def run():
        last = None
        for i in range(80):
            try:
                return f(i)
            except AssertionError as e:
                last = e
        raise SystemExit("no seed for %s: %r" % (f.__name__, last))
    B.append(run)
    return f


def jl(rows):
    return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)


def L(*rows):
    return "".join(r + "\n" for r in rows)


def is_zh(text):
    return len(re.findall(r"[一-鿿]", text)) >= 4


def forms(s):
    """Spellings of one number string: plain, thousands-grouped, trailing zeros trimmed."""
    s = str(s)
    out = []

    def add(x):
        if x not in out:
            out.append(x)

    def group(x):
        w, _, f = x.partition(".")
        return format(int(w), ",") + ("." + f if f else "")
    add(s)
    add(group(s))
    if "." in s:
        t = s.rstrip("0").rstrip(".")
        add(t)
        add(group(t))
    return out


def level_for(n, ref_calls, n_files, multi):
    if n == 0 and ref_calls <= 3:
        return "L0"
    if n == 1 and ref_calls <= 4 and not multi:
        return "L1"
    if n == 2 or (n == 1 and (n_files >= 3 or ref_calls >= 5)):
        return "L2"
    return "L3"


def guard(files):
    d = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    return ("import hashlib, json\n"
            "case = json.load(open(\"case.json\"))\n"
            "_pin = hashlib.sha256(json.dumps(case[\"files\"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()\n"
            "assert _pin == %r, \"fixture changed\"\n" % d)


def policy_for(cid, forbid_calc):
    n = int(cid.split("-")[1])
    must = ["bash", READS[n % 3]]
    p = {"must_offer": must, "never_offer": list(NOWEB)}
    if forbid_calc:
        p["never_offer"] += ["calculator", "data_query"]
    return p


def retry(fn, tries=60):
    for i in range(tries):
        try:
            return fn(i)
        except AssertionError as e:  # noqa: PERF203
            last = e
    raise SystemExit("no seed: %s (%s)" % (fn.__name__, last))


def run_reference(sidecar, files, commands, want):
    root = os.path.realpath(tempfile.mkdtemp(prefix="b21g-ref-"))
    try:
        for path, content in files.items():
            t = os.path.join(root, path)
            os.makedirs(os.path.dirname(t), exist_ok=True)
            with open(t, "w", encoding="utf-8") as f:
                f.write(content)
        stdout = ""
        for c in commands:
            r = sidecar.run(root, c)
            if r.get("error") or r.get("exit_code") not in (0, 1):
                return "`%s` -> %s" % (c, str(r)[:300])
            stdout = r["stdout"]

        def read(path):
            sidecar.next += 1
            sidecar.proc.stdin.write(json.dumps({"id": sidecar.next, "root": root, "op": "read", "path": path}) + "\n")
            sidecar.proc.stdin.flush()
            rep = json.loads(sidecar.proc.stdout.readline())
            return None if rep.get("error") else base64.b64decode(rep["data"]).decode("utf-8")
        return want(stdout, read)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def emit(cid, *, sub, task_type, desc, files, turns, solve, traps, ref, notes_traps, notes_ref, unique,
         forbid_calc=False, axes=("OBS",), nomod=(), req_bash=True):
    """turns: list of {"prompt":..., "req": optional required_tools override}.
    solve(files) -> {"turns":[{"number":str|int,"items":[...]}], "decoys":{trap: str}, "files":{path: text}?}
    ref: (commands, which turn the commands answer (last), ) the reference replays all commands and
    checks the last turn's answer (and files) against solve."""
    ans = solve(files)
    assert len(ans["turns"]) == len(turns), cid
    wfiles = ans.get("files") or {}
    anyform = any(len(forms(t["number"])) > 1 for t in ans["turns"]) and not wfiles
    tl = []
    for i, (t, a) in enumerate(zip(turns, ans["turns"])):
        e = {}
        if req_bash and i == 0:
            e["required_tools"] = ["bash"]
        num = str(a["number"])
        items = [x for x in a["items"] if len(x) > 1]
        if anyform:
            e["output_contains_any"] = forms(num)
            e["output_contains_any_token"] = True
            if items:
                e["output_contains"] = items
                e["output_contains_token"] = True
        else:
            e["output_contains"] = [num] + items
            e["output_contains_token"] = True
        if t.get("excl"):
            e["output_excludes"] = list(t["excl"])
        tl.append({"prompt": t["prompt"], "expect": e})
    for trap in traps:
        d = ans["decoys"].get(trap)
        if d is not None:
            assert all(str(d) != str(a["number"]) for a in ans["turns"]), (cid, trap, d)
        elif not wfiles:
            raise AssertionError("decoy needed for %s" % trap)
    axes = list(dict.fromkeys(list(axes) + [TRAP_AXIS[t] for t in traps]))
    case_expect = None
    if wfiles:
        rules = {}
        for p, txt in files.items():
            rules[p] = {"equals": wfiles[p]} if p in wfiles else {"unchanged": True}
        for p, txt in wfiles.items():
            rules[p] = {"equals": txt}
        case_expect = {"files": rules}
    # verify.py
    body = re.sub(r"def \w+\(", "def solve(", textwrap.dedent(inspect.getsource(solve)), count=1)
    src = guard(files) + "import re\n" + body + "\nans = solve(case[\"files\"])\n"
    if wfiles:
        src += "print(json.dumps({\"files\": ans[\"files\"]}, ensure_ascii=False))\n"
    elif anyform:
        src += textwrap.dedent(inspect.getsource(forms)) + "out = []\nfor t in ans[\"turns\"]:\n    for f in forms(t[\"number\"]):\n        if f not in out:\n            out.append(f)\nprint(json.dumps({\"expected_contains_any\": out}))\n"
    else:
        src += "n = ans[\"turns\"][-1][\"number\"]\nprint(json.dumps({\"expected_number\": float(n) if \".\" in str(n) else int(n)}))\n"
    n_files = len(files)
    multi = len(turns) > 1
    ref_calls = len(ref[0])
    level = level_for(len(traps), ref_calls, n_files, multi)
    forbid_calc = forbid_calc or int(cid.split("-")[1]) % 3 == 0
    pol = policy_for(cid, forbid_calc)
    fam = "b21g-%s-%s" % (sub, cid.split("-")[1])
    notes = "## Traps\n" + "".join("- %s\n" % x for x in notes_traps)
    notes += "\n## Reference solution\n" + "".join("%d. %s\n" % (i, s) for i, s in enumerate(notes_ref, 1))
    notes += "Reference commands (replayed in the sandbox): " + " ;; ".join(ref[0]) + "\n"
    notes += "Final answer: " + "; ".join("turn %d -> %s %s" % (i + 1, a["number"], " ".join(a["items"])) for i, a in enumerate(ans["turns"])) + "\n"
    notes += "\n## Why the answer is unique\n" + unique + "\n"
    BATCH.write_case(cid, desc=desc, task_type=task_type, family=fam, level=level, ref_calls=ref_calls, files=files,
                     turns=tl, verify=src, notes=notes, traps=list(traps), decoys={t: ans["decoys"].get(t) for t in traps},
                     axes=axes, case_expect=case_expect, answer_style="natural", tool_policy=pol, extra_tags=EXTRA)
    REFS[cid] = (files, ref[0], ans)
    META[cid] = {"sub": sub, "lang": "zh" if is_zh(" ".join(t["prompt"] for t in turns)) else "en",
                 "turns": len(turns), "forbid": forbid_calc, "level": level}
    return ans


def check_refs(sidecar):
    bad = 0
    for cid, (files, cmds, ans) in sorted(REFS.items()):
        last = ans["turns"][-1]
        wf = ans.get("files") or {}

        def want(out, read, last=last, wf=wf):
            if not any(f in out for f in forms(last["number"])):
                return "stdout %r lacks %s" % (out[:200], last["number"])
            for it in last["items"]:
                if it not in out:
                    return "stdout %r lacks %s" % (out[:200], it)
            for p, txt in wf.items():
                got = read(p)
                if got != txt:
                    return "%s = %r want %r" % (p, (got or "")[:200], txt[:200])
            return None
        err = run_reference(sidecar, files, cmds, want)
        print("%-10s %s" % (cid, "ok" if err is None else "FAIL: " + err))
        bad += err is not None
    return bad

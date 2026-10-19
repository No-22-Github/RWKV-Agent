"""b22e (v2.2: big files, look at the size first; ids 34401-34450) shared framework.

make() writes case.json / verify.py / NOTES.md. truth is python source over `files`
that sets `answers` (one item per turn: list[str] for kind "s", int for "i", float for "f").
Reference bash commands are replayed in the just-bash sidecar on every build.
"""
import hashlib
import json
import os
import random
import re
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from casegen import Batch, Sidecar  # noqa: E402

BATCH = Batch(salt="b22e", author="llm:claude-sonnet-b22e", version="v2.2", tool_catalog="work-v3")
META = {}
CHECKS = []
MAX_BYTES = 500 * 1024


def rng(seed):
    return random.Random("b22e-%s" % seed)


def is_zh(t):
    return len(re.findall(r"[一-鿿]", t)) >= 4


def forms(v, dp):
    if dp == 0:
        s = str(int(round(v)))
        out = [s]
        if abs(int(s)) >= 1000:
            out.append("{:,}".format(int(s)))
        return out
    s = "%.*f" % (dp, v)
    whole, _, frac = s.partition(".")
    out = [s, "{:,}".format(int(whole)) + "." + frac if int(whole) else s]
    t = s.rstrip("0").rstrip(".")
    out.append(t)
    if int(whole) >= 1000:
        out.append("{:,}".format(int(whole)) + "." + frac.rstrip("0") if frac.rstrip("0") else "{:,}".format(int(whole)))
    return list(dict.fromkeys(out))


def allowed(n_traps, ref_calls, n_files, multi):
    v = set()
    if n_traps == 0 and ref_calls <= 3:
        v.add("L0")
    if n_traps == 1 and ref_calls <= 4:
        v.add("L1")
    if n_traps == 2 or (n_traps == 1 and (n_files >= 3 or ref_calls >= 5)):
        v.add("L2")
    if n_traps >= 3 or (multi and n_traps >= 1) or ref_calls >= 8:
        v.add("L3")
    return v


def guard(files):
    d = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    return ("import hashlib, json\n"
            "case = json.load(open(\"case.json\"))\n"
            "files = case[\"files\"]\n"
            "_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()\n"
            "assert _pin == %r, \"fixture changed\"\n" % d)


def T(prompt, kind="s", req=("bash",), exc=(), dp=2):
    return dict(prompt=prompt, kind=kind, req=list(req), exc=list(exc), dp=dp)


def check_shape(cid, files, shape):
    total = sum(len(v.encode()) for v in files.values())
    assert total <= MAX_BYTES, (cid, total)
    if shape == "log":
        for p, t in files.items():
            n = t.count("\n")
            assert 2000 <= n <= 5000, (cid, p, n)
            assert max(len(l) for l in t.split("\n")) <= 120, (cid, p)
    elif shape == "csv":
        for p, t in files.items():
            n = t.count("\n")
            assert 2000 <= n <= 4000, (cid, p, n)
    elif shape == "dir":
        assert len(files) >= 300, (cid, len(files))


def make(cid, *, sub, task_type, desc, files, turns, truth, ref, notes, shape, traps=("TR-TRUNC",), axes=("LNG",),
         rc=4, policy=None, deep=True, extra_exc=None):
    check_shape(cid, files, shape)
    ns = {"files": files}
    exec(truth, ns)
    answers = ns["answers"]
    assert len(answers) == len(turns), cid
    tl = []
    anyforms = []
    for t, a in zip(turns, answers):
        e = {}
        if t["req"]:
            e["required_tools"] = list(t["req"])
        if t["kind"] == "s":
            assert a and all(isinstance(x, str) and len(x) > 1 for x in a), (cid, a)
            e["output_contains"] = list(a)
            if any(x.isdigit() for x in a) and all(x.isascii() for x in a):
                e["output_contains_token"] = True
            if deep:
                for x in a:
                    if not x.isdigit():
                        for p, tx in files.items():
                            head = "\n".join(tx.split("\n")[:200])
                            assert x not in head, (cid, "answer visible on first screen", x, p)
        else:
            fl = forms(a, 0 if t["kind"] == "i" else t["dp"])
            e["output_contains_any"] = fl
            e["output_contains_any_token"] = True
            anyforms += [x for x in fl if x not in anyforms]
        if t["exc"]:
            e["output_excludes"] = list(t["exc"])
        tl.append({"prompt": t["prompt"], "expect": e})
    for cmd, want in ref:
        CHECKS.append((cid, cmd, files, want, answers))
    multi = len(turns) > 1
    ok = sorted(x for x in allowed(len(traps), rc, len(files), multi) if x != "L0")
    level = ok[0]
    # verify.py: recompute from fixture
    body = truth + "\n"
    s_first = next((a for t, a in zip(turns, answers) if t["kind"] == "s"), None)
    if s_first is not None:
        f0 = s_first[0]
        if f0.isdigit():
            body += "print(json.dumps({\"expected_number\": float(answers[%d][0])}))\n" % [t["kind"] for t in turns].index("s")
        else:
            body += "print(json.dumps({\"expected_string\": answers[%d][0]}, ensure_ascii=False))\n" % [t["kind"] for t in turns].index("s")
    else:
        body += ("from __main__ import *\n" if False else "") + (
            "KINDS = %r\nDPS = %r\n" % ([t["kind"] for t in turns], [t["dp"] for t in turns]) +
            FORMS_SRC +
            "out = []\nfor k, dp, a in zip(KINDS, DPS, answers):\n"
            "    out += [x for x in forms(a, 0 if k == 'i' else dp) if x not in out]\n"
            "print(json.dumps({\"expected_contains_any\": out}, ensure_ascii=False))\n")
    shown = "; ".join(("/".join(a) if isinstance(a, list) else str(a)) for a in answers)
    nt = "## Traps\n%s\n\n## Reference solution\n%s\n\n## Why the answer is unique\n%s Expected answer per turn: %s.\n" % (
        notes["traps"], notes["steps"], notes["unique"], shown)
    tools_pol = policy or {"must_offer": ["bash", "read_file"]}
    ce = {"max_calls": {"read_file": 3}}
    num = cid.split("-")[1]
    BATCH.write_case(cid, desc=desc, task_type=task_type, family="b22e-%s-%06d" % (sub, int(num)), level=level,
                     ref_calls=rc, files=files, turns=tl, verify=guard(files) + body, notes=nt, traps=list(traps),
                     decoys={t: "0" for t in traps}, axes=list(axes), answer_style="natural", tool_policy=tools_pol,
                     extra_tags={"batch": "b22e", "subtype": sub}, case_expect=ce)
    META[cid] = {"sub": sub, "lang": "zh" if is_zh(" ".join(t["prompt"] for t in turns)) else "en",
                 "turns": len(turns), "level": level, "plen": sum(len(t["prompt"]) for t in turns) / len(turns),
                 "bytes": sum(len(v.encode()) for v in files.values()), "files": len(files),
                 "lines": max(v.count("\n") for v in files.values())}


FORMS_SRC = '''
def forms(v, dp):
    if dp == 0:
        s = str(int(round(v)))
        out = [s]
        if abs(int(s)) >= 1000:
            out.append("{:,}".format(int(s)))
        return out
    s = "%.*f" % (dp, v)
    whole, _, frac = s.partition(".")
    out = [s, "{:,}".format(int(whole)) + "." + frac if int(whole) else s]
    t = s.rstrip("0").rstrip(".")
    out.append(t)
    if int(whole) >= 1000:
        out.append("{:,}".format(int(whole)) + "." + frac.rstrip("0") if frac.rstrip("0") else "{:,}".format(int(whole)))
    return list(dict.fromkeys(out))
'''


def run_checks():
    sc = Sidecar()
    bad = []
    for cid, cmd, files, want, answers in CHECKS:
        root = os.path.realpath(tempfile.mkdtemp(prefix="b22e-"))
        try:
            for p, t in files.items():
                tg = os.path.join(root, p)
                os.makedirs(os.path.dirname(tg) or root, exist_ok=True)
                with open(tg, "w", encoding="utf-8", newline="") as f:
                    f.write(t)
            r = sc.run(root, cmd)
            out = r.get("stdout") or ""
            w = want(answers) if callable(want) else want
            if r.get("error") or r.get("exit_code") not in (0, 1) or not re.search(r"(?<![\w.])(?<!\d,)" + re.escape(w) + r"(?![\w]|\.\d)", out):
                bad.append((cid, cmd, w, str(r)[:300]))
        finally:
            shutil.rmtree(root, ignore_errors=True)
    sc.close()
    return bad

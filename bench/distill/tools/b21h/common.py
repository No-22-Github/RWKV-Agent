"""b21h (v2.1: empty result / failed command -> look for the cause first) shared framework.

Each case: fixture files, turns (prompt, inc, exc), a truth snippet (python, sets `ans`
from `files`), reference bash commands (must print the right answer in the sandbox) and
"lazy" commands (the obvious first command; must give empty / 0 / error in the sandbox).
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

BATCH = Batch(salt="b21h", author="llm:claude-sonnet-b21h", version="v2.1", tool_catalog="work-v2")
EXTRA = {"batch": "b21h"}
META = {}
CHECKS = []          # (cid, kind, command, files)
SIDE = []

BASE = {"must_offer": ["bash", "read_file"]}
NOCALC = {"must_offer": ["bash", "read_file"], "never_offer": ["calculator", "data_query"]}
TRAP_OF = {"fmt": "TR-NUMFMT", "col": "TR-DELIM", "file": "TR-NEARNAME", "term": "TR-DEFN", "cmd": "TR-DEFN"}


def is_zh(t):
    return len(re.findall(r"[一-鿿]", t)) >= 4


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


def L(*rows):
    return "".join(r + "\n" for r in rows)


def make(cid, *, sub, task_type, desc, files, turns, truth, ref, lazy, notes, policy=None, trap=None,
         multi_note="", extra_traps=()):
    """turns: list of (prompt, inc, exc). truth: python source setting `ans` (first turn's first inc item).
    ref: list of (command, substring that must be in stdout) – one per turn answer.
    lazy: list of (command, kind) kind in empty|zero|err."""
    trap = trap or TRAP_OF[sub]
    traps = [trap] + list(extra_traps)
    ns = {"files": files}
    exec(truth, ns)
    first = turns[0][1][0]
    assert str(ns["ans"]) == first, (cid, ns["ans"], first)
    for c, want in ref:
        CHECKS.append((cid, "ref", c, files, want))
    for c, kind in lazy:
        CHECKS.append((cid, kind, c, files, None))
    multi = len(turns) > 1
    rc = 5 if (multi or sub in ("cmd", "file")) else 4
    ok = sorted(x for x in allowed(len(traps), rc, len(files), multi) if x != "L0")
    level = ok[0]
    tl = []
    for p, inc, exc in turns:
        e = {"output_contains": list(inc)}
        assert all(len(x) > 1 for x in inc), (cid, inc)
        exc = [x for x in (exc or []) if re.search(r"0|zero|零", x)]   # no negation phrases: they hit honest "not found by X, found by Y" answers
        if exc:
            e["output_excludes"] = list(exc)
        if not any(re.search(r"[一-鿿]", x) for x in inc):
            e["output_contains_token"] = True
        for x in inc:
            assert cid in ("cfg-32320", "cfg-32327", "cfg-32330") or not (re.fullmatch(r"\d+", x) and int(x) >= 1000), (cid, x)
        tl.append({"prompt": p, "expect": e})
    body = truth + "\nprint(json.dumps({%s: ans}, ensure_ascii=False))\n" % (
        '"expected_number"' if re.fullmatch(r"-?\d+(\.\d+)?", first) else '"expected_string"')
    if re.fullmatch(r"-?\d+(\.\d+)?", first):
        body = body.replace("ans}", "float(ans)}")
    n = notes
    nt = "## Traps\n%s\n\n## Reference solution\n%s\n\n## Why the answer is unique\n%s\nExpected: %s\n" % (
        n["traps"], n["steps"], n["unique"], "; ".join(x for _, i, _ in turns for x in i))
    zh = is_zh(" ".join(t[0] for t in turns))
    pol = policy if policy is not None else BASE
    BATCH.write_case(cid, desc=desc, task_type=task_type, family="b21h-%s-%s" % (sub, cid.split("-")[1]),
                     level=level, ref_calls=rc, files=files, turns=tl, verify=guard(files) + body, notes=nt,
                     traps=traps, decoys={t: "0" for t in traps}, axes=["OBS", "VER"] + (["ERR"] if sub == "file" else []),
                     answer_style="natural", tool_policy=pol, extra_tags=EXTRA)
    META[cid] = {"sub": sub, "lang": "zh" if zh else "en", "turns": len(turns), "pol": "nocalc" if pol is NOCALC else "base"}


def run_checks():
    from casegen import check_reference  # noqa
    sc = Sidecar()
    bad = []
    for cid, kind, cmd, files, want in CHECKS:
        root = os.path.realpath(tempfile.mkdtemp(prefix="b21h-"))
        try:
            for p, t in files.items():
                tg = os.path.join(root, p)
                os.makedirs(os.path.dirname(tg), exist_ok=True)
                with open(tg, "w", encoding="utf-8", newline="") as f:
                    f.write(t)
            r = sc.run(root, cmd)
            out = (r.get("stdout") or "").strip()
            code = r.get("exit_code")
            if kind == "ref":
                if r.get("error") or code not in (0, 1) or want not in out:
                    bad.append((cid, "ref", cmd, want, r))
            elif kind == "empty":
                if r.get("error") or out != "":
                    bad.append((cid, "lazy-empty", cmd, r))
            elif kind == "zero":
                if r.get("error") or out != "0":
                    bad.append((cid, "lazy-zero", cmd, r))
            elif kind == "err":
                if r.get("error") or code == 0:
                    bad.append((cid, "lazy-err", cmd, r))
        finally:
            shutil.rmtree(root, ignore_errors=True)
    sc.close()
    return bad


NAMES = ["Mei Lindqvist", "Tomas Okafor", "Ravi Castellano", "Hana Brodsky", "Jonas Wirth", "Ines Marchetti", "Kofi Larsen",
         "Yuki Bernard", "Ola Petrov", "Sana Duarte", "Elif Novak", "Arjun Holm", "Lena Quartey", "Marek Silva", "Nadia Fenwick"]
CITIES = ["Oslo", "Lyon", "Porto", "Gdansk", "Bremen", "Turin", "Ghent", "Bergen"]


def rng(seed):
    return random.Random("b21h-%s" % seed)


def csv(header, rows, sep=",", eol="\n"):
    return eol.join([sep.join(header)] + [sep.join(str(c) for c in r) for r in rows]) + eol


FIRST = ["Mei", "Tomas", "Ravi", "Hana", "Jonas", "Ines", "Kofi", "Yuki", "Ola", "Sana", "Elif", "Arjun", "Lena", "Marek", "Nadia", "Piotr", "Greta", "Omar", "Vera", "Dario"]
LAST = ["Lindqvist", "Okafor", "Castellano", "Brodsky", "Wirth", "Marchetti", "Larsen", "Bernard", "Petrov", "Duarte", "Novak", "Holm", "Quartey", "Silva", "Fenwick", "Aalto", "Brandt", "Costa", "Dvorak", "Ek"]


def people(r, n):
    allp = ["%s %s" % (a, b) for a in FIRST for b in LAST]
    r.shuffle(allp)
    return allp[:n]


WORDS = ["amber", "birch", "cedar", "delta", "ember", "flint", "grove", "haven", "iris", "jade", "kelp", "lumen", "maple", "nova", "onyx", "pearl"]


def filler_keys(r, n, avoid=()):
    out = []
    while len(out) < n:
        k = "%s_%s_%s" % (r.choice(WORDS), r.choice(WORDS), r.choice(["limit", "mode", "path", "name", "level", "size"]))
        if k not in out and not any(a in k for a in avoid):
            out.append(k)
    return out

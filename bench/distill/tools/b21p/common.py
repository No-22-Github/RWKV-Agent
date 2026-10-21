"""b21p (v2.1 wave 3: filesystem + logs, ids 33701-33770) shared framework.

Each case: fixture files, turns, a truth snippet (python over `files`, sets `answers`
list = first expected string of each turn) and reference bash commands that are replayed
in the just-bash sandbox (must print the answer). Re-running writes identical files.
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

BATCH = Batch(salt="b21p", author="llm:claude-sonnet-b21p", version="v2.1", tool_catalog="agent-tool-v2.0")
EXTRA = {"batch": "b21p"}
META = {}
CHECKS = []

BASH = {"must_offer": ["bash", "read_file"]}
BASH_ONLY = {"must_offer": ["bash"]}
FREE = None   # no tool_policy: random directory (only for cases solvable with list/read/search)
LISTREAD = {"must_offer": ["list_files", "read_file"]}

NEG_ZH = ["没有", "不存在", "未找到", "找不到", "没找到", "不在", "没发现", "未发现", "查不到", "缺少", "并无", "没看到", "不见"]
NEG_EN = ["not found", "no such", "does not exist", "doesn't exist", "not exist", "no file", "missing", "couldn't find",
          "could not find", "isn't there", "not present", "don't see", "did not find", "didn't find", "cannot find",
          "can't find", "there is no", "there's no", "no match", "absent"]
_extra = ["not exist", "doesn't contain", "does not contain", "no identical", "no duplicate", "none", "nothing", "no two", "not identical", "are all different", "all different", "不重复", "没有重复", "各不相同", "都不一样", "都不同", "没有相同", "无重复"]
NEG = NEG_ZH + NEG_EN + _extra
NEG = NEG + [x.capitalize() for x in NEG_EN + _extra if x.isascii()]
NEG = NEG + [x.replace("'", "\u2019") for x in NEG if "'" in x]


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


def T(prompt, inc=(), any_=(), exc=(), req=(), token=None, anytoken=False, forbid=(), syn=False):
    return dict(syn=syn, prompt=prompt, inc=list(inc), any=list(any_), exc=list(exc), req=list(req), token=token,
                anytoken=anytoken, forbid=list(forbid))


def make(cid, *, sub, task_type, desc, files, turns, truth, notes, ref=(), lazy=(), policy=BASH, traps=("TR-DECOY",),
         expect_files=None, rc=4, axes=("OBS",), max_calls=None):
    """turns: list of T(). truth: python source setting `answers` (list of str, one per turn that has a
    checkable answer) or, for write cases, nothing. ref: (command, substring) replayed in the sandbox.
    lazy: (command, kind) kind in empty|zero|err."""
    traps = list(traps)
    ns = {"files": files}
    exec(truth, ns)
    answers = ns.get("answers", [])
    keyed = [t for t in turns if t["inc"] or (t["any"] and not t["syn"] and t["any"][0] != NEG_ZH[0])]
    if answers:
        assert 0 < len(answers) <= len(keyed), (cid, answers)
        for a, t in zip(answers, keyed):
            assert str(a) in t["inc"] + t["any"], (cid, a, t["inc"], t["any"])
    for c, want in ref:
        CHECKS.append((cid, "ref", c, files, want))
    for c, kind in lazy:
        CHECKS.append((cid, kind, c, files, None))
    multi = len(turns) > 1
    if multi:
        rc = max(rc, 5)
    ok = sorted(x for x in allowed(len(traps), rc, len(files), multi) if x != "L0") or sorted(allowed(len(traps), rc, len(files), multi))
    level = ok[0]
    tl = []
    for t in turns:
        e = {}
        if t["req"]:
            e["required_tools"] = list(t["req"])
        if t["forbid"]:
            e["forbidden_tools"] = list(t["forbid"])
        if t["inc"]:
            e["output_contains"] = list(t["inc"])
        if t["any"]:
            e["output_contains_any"] = list(t["any"])
        if t["exc"]:
            e["output_excludes"] = list(t["exc"])
        tok = t["token"]
        if tok is None:
            tok = bool(t["inc"]) and not any(re.search(r"[一-鿿]", x) for x in t["inc"]) and any(re.fullmatch(r"\d{1,3}", x) for x in t["inc"])
        if tok:
            e["output_contains_token"] = True
        if t["anytoken"]:
            e["output_contains_any_token"] = True
        for x in t["inc"]:
            assert len(x) > 1 or re.fullmatch(r"\d", x), (cid, x)
        tl.append({"prompt": t["prompt"], "expect": e})
    ce = None
    if expect_files:
        ce = {"files": expect_files}
        if max_calls:
            ce["max_calls"] = max_calls
    first = (turns[0]["inc"] or turns[0]["any"] or [""])[0]
    if expect_files:
        body = ("exp = case[\"expect\"][\"files\"]\n"
                "for path, rule in exp.items():\n"
                "    if rule.get(\"unchanged\") or rule.get(\"absent\"):\n"
                "        assert path in case[\"files\"], path\n"
                "print(json.dumps({\"files\": {p: (r[\"equals\"] if \"equals\" in r else case[\"files\"][p]) for p, r in exp.items() if not r.get(\"absent\")}}, ensure_ascii=False))\n")
    elif not answers:
        last_any = [t for t in turns if t["any"]][-1]["any"]
        body = truth + "\nprint(json.dumps({\"expected_contains_any\": %s}, ensure_ascii=False))\n" % json.dumps(last_any, ensure_ascii=False)
    else:
        incs = [x for t in turns for x in t["inc"]]
        pick = next((i for i, a in enumerate(answers) if str(a) in incs), 0)
        first = str(answers[pick])
        isnum = bool(re.fullmatch(r"-?\d+(\.\d+)?", first))
        body = truth + "\nprint(json.dumps({%s: %s}, ensure_ascii=False))\n" % (
            '"expected_number"' if isnum else '"expected_string"', ("float(answers[%d])" if isnum else "answers[%d]") % pick)
    nt = "## Traps\n%s\n\n## Reference solution\n%s\n\n## Why the answer is unique\n%s\n" % (
        notes["traps"], notes["steps"], notes["unique"])
    zh = is_zh(" ".join(t["prompt"] for t in turns))
    BATCH.write_case(cid, desc=desc, task_type=task_type, family="b21p-%s-%s" % (sub, cid.split("-")[1]),
                     level=level, ref_calls=rc, files=files, turns=tl, verify=guard(files) + body, notes=nt,
                     traps=traps, decoys={t: "0" for t in traps}, axes=list(axes), answer_style="natural",
                     tool_policy=policy, extra_tags=EXTRA, case_expect=ce)
    META[cid] = {"sub": sub, "lang": "zh" if zh else "en", "turns": len(turns),
                 "pol": "none" if policy is None else "set"}


def run_checks():
    sc = Sidecar()
    bad = []
    for cid, kind, cmd, files, want in CHECKS:
        root = os.path.realpath(tempfile.mkdtemp(prefix="b21p-"))
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
            elif kind == "empty" and (r.get("error") or out != ""):
                bad.append((cid, "lazy-empty", cmd, r))
            elif kind == "zero" and (r.get("error") or out != "0"):
                bad.append((cid, "lazy-zero", cmd, r))
            elif kind == "err" and (r.get("error") or code == 0):
                bad.append((cid, "lazy-err", cmd, r))
        finally:
            shutil.rmtree(root, ignore_errors=True)
    sc.close()
    return bad


def rng(seed):
    return random.Random("b21p-%s" % seed)


def L(*rows):
    return "".join(r + "\n" for r in rows)


WORDS = ("alpha river stone lamp cedar quartz maple orbit pixel ember harbor delta fjord grain hollow ivory juniper "
         "kettle lantern meadow nectar oyster pebble quill ridge saddle thistle umber velvet willow yarrow zephyr").split()


def blob(r, n, tag=""):
    """ASCII text of exactly n bytes (lines of words), unique per rng state."""
    out = []
    size = 0
    while size < n:
        line = " ".join(r.choice(WORDS) for _ in range(r.randint(3, 8)))
        if tag and not out:
            line = tag + " " + line
        out.append(line)
        size += len(line) + 1
    s = "\n".join(out) + "\n"
    s = s[:n - 1] + "\n" if len(s) >= n else s
    s = s[:n]
    assert len(s.encode()) == n
    if not s.endswith("\n"):
        s = s[:-1] + "\n"
    return s


def sha(s):
    return hashlib.sha256(s.encode()).hexdigest()

"""b20c shared helpers: case writer wrapper, refusal word list, bash reference replay."""
import base64
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from casegen import Batch, Sidecar, lines  # noqa: E402,F401

BATCH = Batch(salt="b20c", author="llm:claude-sonnet-b20c", version="v2.0", tool_catalog="work-v2")
REFS = {}   # cid -> (files, commands, check)
META = {}   # cid -> dict(sub, lang, turns, never)
NOWEB = ["web_search", "web_fetch"]

_ZH = ["无法联网", "不能联网", "没法联网", "没办法联网", "没有联网", "无法实时", "没法实时", "无法获取", "无法查询", "查询不了",
       "查不了", "无法核实", "未能核实", "无法确认", "无法验证", "无法查证", "没有网络", "无法访问", "不能访问", "无法上网",
       "未核实", "未经核实", "没法核实", "没办法核实", "无法实时查询", "无法查到", "查不到", "没有查询天气", "没有天气查询",
       "无法提供", "没法提供", "不能提供", "无法给出", "没办法提供", "无法直接", "不能直接", "没有直接", "历史报价", "可能已有调整"]
_EN = ["cannot", "can't", "can not", "unable", "not able", "don't have access", "do not have access", "no internet",
       "no web", "not connected", "couldn't", "could not", "unverified", "not verified", "no way to", "don't have a way",
       "do not have a way", "no live", "no real-time", "without internet", "isn't available", "is not available", "aren't able",
       "I'm unable", "don't have the ability", "do not have the ability"]


def cant_words():
    out = list(_ZH)
    for w in _EN:
        out += [w, w.capitalize(), w.replace("'", "’"), w.capitalize().replace("'", "’")]
    return list(dict.fromkeys(out))


def expand(words):
    out = []
    for w in words:
        out += [w, w.capitalize(), w.replace("'", "’"), w.capitalize().replace("'", "’")]
    return list(dict.fromkeys(out))


def is_zh(text):
    return len(re.findall(r"[一-鿿]", text)) >= 4


def level_for(traps, ref_calls, n_files, multi):
    n = len(traps)
    if n == 0 and ref_calls <= 3:
        return "L0"
    if n == 1 and ref_calls <= 4:
        return "L1"
    if n == 2 or (n == 1 and (n_files >= 3 or ref_calls >= 5)):
        return "L2"
    if n >= 3 or (multi and n >= 1) or ref_calls >= 8:
        return "L3"
    raise ValueError("no level traps=%d ref=%d" % (n, ref_calls))


def guard(files):
    d = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    return ("import hashlib, json, re\n"
            "case = json.load(open(\"case.json\"))\n"
            "_pin = hashlib.sha256(json.dumps(case[\"files\"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()\n"
            "assert _pin == %r, \"fixture changed\"\n" % d)


def mk(cid, *, sub, task_type, desc, files, turns, never, must, traps_notes, ref_text, why, body,
       traps=(), decoys=None, ref_calls=2, case_expect=None, ref=None, axes=("DEC",), web=None):
    """turns: [(prompt, expect)]. body: verify.py code after the fixture guard."""
    assert not set(never) & set(must), cid
    for _, e in turns:
        assert set(e.get("required_tools", [])) <= set(must), (cid, e)
    multi = len(turns) > 1
    level = level_for(traps, ref_calls, len(files), multi)
    tl = [{"prompt": p, "expect": e} for p, e in turns]
    notes = "## Traps\n" + "".join("- %s\n" % t for t in traps_notes)
    notes += "\n## Reference solution\n" + ref_text.strip("\n") + "\n"
    notes += "\n## Why the answer is unique\n" + why.strip("\n") + "\n"
    if cid.split("-")[0] in ("web", "hyb"):
        p0 = turns[0][0]
        alts = ["%s" % p0, "Quick question: %s" % p0, "%s (a short answer is fine)" % p0, "Hi, %s" % p0, "One more thing: %s" % p0]
        notes += "\n## Five alternative phrasings of the task\n" + "".join("%d. %s\n" % (i + 1, a) for i, a in enumerate(alts))
    BATCH.write_case(cid, desc=desc, task_type=task_type, family="fam-" + sub, level=level, ref_calls=ref_calls,
                     files=files, turns=tl, verify=guard(files) + body.strip("\n") + "\n", notes=notes,
                     traps=traps, decoys=decoys if decoys is not None else {t: None for t in traps},
                     axes=list(axes), case_expect=case_expect, web=web,
                     tool_policy={"must_offer": list(must), "never_offer": list(never)},
                     extra_tags={"batch": "b20c", "sub": sub})
    META[cid] = {"sub": sub, "zh": is_zh(" ".join(p for p, _ in turns)), "turns": len(turns),
                 "never": list(never), "must": list(must)}
    if ref:
        REFS[cid] = (files, ref[0], ref[1])


# ---- expectation builders
def refuse(forbid, *, contains=(), excludes=(), token=False, required=(), words=None):
    e = {"forbidden_tools": list(forbid), "output_contains_any": list(words) if words is not None else cant_words()}
    if contains:
        e["output_contains"] = list(contains)
        if token:
            e["output_contains_token"] = True
    if excludes:
        e["output_excludes"] = list(excludes)
    if required:
        e["required_tools"] = list(required)
    return e


def value(vals, *, token=False, required=(), forbid=(), any_forms=None, any_token=True):
    e = {}
    if any_forms:
        e["output_contains_any"] = list(any_forms)
        if any_token:
            e["output_contains_any_token"] = True
    else:
        e["output_contains"] = list(vals)
        if token:
            e["output_contains_token"] = True
    if required:
        e["required_tools"] = list(required)
    if forbid:
        e["forbidden_tools"] = list(forbid)
    return e


# ---- bash reference replay (sidecar is copy-on-write: read overlay via op)
def run_ref(sc, files, commands, want):
    root = os.path.realpath(tempfile.mkdtemp(prefix="b20c-ref-"))
    try:
        for p, c in files.items():
            t = os.path.join(root, p)
            os.makedirs(os.path.dirname(t), exist_ok=True)
            open(t, "w", encoding="utf-8").write(c)
        out = ""
        for cmd in commands:
            r = sc.run(root, cmd)
            if r.get("error") or r.get("exit_code") not in (0, 1):
                return "`%s` -> %s" % (cmd, r)
            out = r["stdout"]

        def read(path):
            sc.next += 1
            sc.proc.stdin.write(json.dumps({"id": sc.next, "root": root, "op": "read", "path": path}) + "\n")
            sc.proc.stdin.flush()
            rep = json.loads(sc.proc.stdout.readline())
            if rep.get("error"):
                return None
            return base64.b64decode(rep["data"]).decode("utf-8")
        return want(out, read)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def has(*needles):
    def check(out, _read):
        return None if all(n in out for n in needles) else "stdout %r lacks %s" % (out[:300], needles)
    return check


def file_eq(path, text):
    def check(_out, read):
        got = read(path)
        return None if got == text else "%s = %r" % (path, (got or "")[:200])
    return check


FORMS = ('f = ["%.2f" % s]\nf.append(f[0].rstrip("0").rstrip("."))\ng = "{:,}".format(int(f[0].split(".")[0])) + "." + f[0].split(".")[1]\n'
         'f += [g, g.rstrip("0").rstrip(".")]\nprint(json.dumps({"expected_contains_any": list(dict.fromkeys(f))}))\n')

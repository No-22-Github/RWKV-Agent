"""b21n (v2.1: small code repositories, ids 33501-33570) shared framework.

make() takes fixture files, turns and a truth snippet (python; sets `ans` or `end_files`)
and writes case.json/verify.py/NOTES.md. Reference shell commands are replayed in the
just-bash sandbox by run_checks() so the grep-style solutions are known to work.
"""
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from casegen import Batch, Sidecar  # noqa: E402

BATCH = Batch(salt="b21n", author="llm:claude-sonnet-b21n", version="v2.1", tool_catalog="agent-tool-v2.0")
EXTRA = {"batch": "b21n"}
META = {}
CHECKS = []

WEB = ["web_search", "web_fetch"]
P_SEARCH = {"must_offer": ["search_text", "read_file"], "never_offer": WEB}
P_BASH = {"must_offer": ["bash", "read_file"], "never_offer": WEB}
P_LINES = {"must_offer": ["list_files", "search_text", "read_lines"]}
P_READ = {"must_offer": ["list_files", "read_file"]}
P_RWL = {"must_offer": ["read_lines", "replace_lines"], "never_offer": WEB}
P_SRW = {"must_offer": ["search_text", "read_file", "write_file"]}
P_SRL = {"must_offer": ["search_text", "read_lines", "replace_lines"]}
P_BW = {"must_offer": ["bash", "read_file", "write_file"]}
P_RO = {"must_offer": ["list_files", "read_file", "write_file"]}
P_RO2 = {"must_offer": ["search_text", "read_file", "replace_lines"], "never_offer": WEB}
WRITE_TOOLS = ["write_file", "replace_lines", "append_file"]

HAN = re.compile(r"[一-鿿]")


def is_zh(t):
    return len(HAN.findall(t)) >= 4


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


def lineno(files, path, needle, nth=1):
    """1-based line number of the nth line of files[path] containing needle."""
    k = 0
    for i, line in enumerate(files[path].split("\n"), 1):
        if needle in line:
            k += 1
            if k == nth:
                return i
    raise AssertionError((path, needle))


def make(cid, *, sub, task_type, desc, files, turns, truth, notes, policy, trap="TR-DECOY", decoy="x",
         ref_calls=4, ops=None, extra_traps=(), refs=(), readonly=False, axes=("OBS",), answer_files=None):
    """turns: list of dicts {p, inc, any?, exc?, req?, forb?}.
    truth: python source (has `files`, optional `ops` applied) that sets `ans` (string/int) for read cases.
    ops: list of ("sub", path, old, new) applied cumulatively (fix cases); expect.files from the result.
    refs: [(command, want_substring)] replayed in the sandbox."""
    traps = [trap] + list(extra_traps)
    for c, want in refs:
        CHECKS.append((cid, c, files, want))
    end = dict(files)
    for op in ops or []:
        _, path, old, new = op
        assert end[path].count(old) == 1, (cid, path, old)
        end[path] = end[path].replace(old, new)
    ns = {"files": files}
    exec(truth, ns)
    multi = len(turns) > 1
    tl = []
    for t in turns:
        e = {}
        inc = list(t.get("inc") or [])
        for x in inc:
            assert len(x) >= 1, (cid, inc)
        if inc:
            e["output_contains"] = inc
            if not any(HAN.search(x) for x in inc):
                e["output_contains_token"] = True
        if t.get("any"):
            e["output_contains_any"] = list(t["any"])
        if t.get("exc"):
            e["output_excludes"] = list(t["exc"])
        if t.get("req"):
            e["required_tools"] = list(t["req"])
        forb = list(t.get("forb") or [])
        if readonly:
            forb = WRITE_TOOLS
        if forb:
            e["forbidden_tools"] = forb
        tl.append({"prompt": t["p"], "expect": e})
    rules = {}
    for p, txt in files.items():
        rules[p] = {"equals": end[p]} if end[p] != txt else {"unchanged": True}
    if ops:
        assert any("equals" in r for r in rules.values()), cid
    first = next((x for t in turns for x in (t.get("inc") or [])), "")
    if ops:
        body = ("OPS = json.loads(%r)\nend = dict(files)\nfor _, path, old, new in OPS:\n"
                "    assert end[path].count(old) == 1, (path, old)\n    end[path] = end[path].replace(old, new)\n"
                "print(json.dumps({\"files\": {p: t for p, t in end.items() if files[p] != t}}, ensure_ascii=False))\n"
                % json.dumps([list(o) for o in ops], ensure_ascii=False))
    else:
        assert str(ns["ans"]) == first, (cid, ns["ans"], first)
        body = truth + "\n"
        if re.fullmatch(r"-?\d+", first):
            body += "print(json.dumps({\"expected_number\": float(ans)}))\n"
        else:
            body += "print(json.dumps({\"expected_string\": ans}, ensure_ascii=False))\n"
    nt = "## Traps\n%s\n\n## Reference solution\n%s\n\n## Why the answer is unique\n%s\nExpected: %s\n" % (
        notes["traps"], notes["steps"], notes["unique"],
        "; ".join(x for t in turns for x in (t.get("inc") or [])) or "(file state)")
    rc = ref_calls
    ok = sorted(x for x in allowed(len(traps), rc, len(files), multi) if x != "L0")
    assert ok, (cid, len(traps), rc, len(files), multi)
    level = ok[0]
    zh = is_zh(" ".join(t["p"] for t in turns))
    axes = list(axes)
    for t_ in traps:
        a_ = {"TR-NEARNAME": "ERR", "TR-MULTISRC": "CHN", "TR-READONLY": "CON", "TR-SUPERSEDE": "VER"}.get(t_)
        if a_ and a_ not in axes:
            axes.append(a_)
    BATCH.write_case(cid, desc=desc, task_type=task_type, family="b21n-%s-%s" % (sub, cid.split("-")[1]),
                     level=level, ref_calls=rc, files=files, turns=tl, verify=guard(files) + body, notes=nt,
                     traps=traps, decoys={t: (None if ops else decoy) for t in traps},
                     axes=axes,
                     answer_style="natural", tool_policy=policy, extra_tags=EXTRA,
                     case_expect={"files": rules})
    META[cid] = {"sub": sub, "lang": "zh" if zh else "en", "turns": len(turns), "level": level,
                 "pol": "+".join(policy["must_offer"])}


def run_checks():
    sc = Sidecar()
    bad = []
    for cid, cmd, files, want in CHECKS:
        root = os.path.realpath(tempfile.mkdtemp(prefix="b21n-"))
        try:
            for p, t in files.items():
                tg = os.path.join(root, p)
                os.makedirs(os.path.dirname(tg), exist_ok=True)
                with open(tg, "w", encoding="utf-8", newline="") as f:
                    f.write(t)
            r = sc.run(root, cmd)
            out = (r.get("stdout") or "").strip()
            if r.get("error") or r.get("exit_code") not in (0, 1) or want not in out:
                bad.append((cid, cmd, want, r))
        finally:
            shutil.rmtree(root, ignore_errors=True)
    sc.close()
    return bad

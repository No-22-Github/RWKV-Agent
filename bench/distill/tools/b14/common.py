"""b14 (v1.42: bash + get_weather "do it right" batch on work-v2) settings and helpers.

The case writer, weather fixture helper and sidecar client come from ../casegen.py.
Two things differ from b12:

* the just-bash sidecar is copy-on-write (native/justbash/sidecar.ts never
  writes host files), so casegen.check_reference cannot see what an edit
  reference did by opening the scratch directory; run_reference here reads the
  overlay back with the sidecar's own `read` op;
* each builder registers its behavior spec (SPEC) and reference (REFS) through
  case(), and the case level is derived from the lint rule instead of typed.
"""
import base64
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from casegen import Batch, Sidecar, lines, weather  # noqa: E402,F401

BATCH = Batch(salt="b14", author="llm:claude-b14", version="v1.42", tool_catalog="work-v2")

SPEC = {}   # case id -> behavior.py spec
REFS = {}   # case id -> (files, commands, check(stdout, read))
META = {}   # case id -> {"sub": ..., "lang": "zh"|"en", "turns": n, "zero_first": bool}

NOWEB = ["web_search", "web_fetch"]
DONE = "DONE"


# ------------------------------------------------------------------ writing


def level_for(traps, ref_calls, n_files, multi):
    """Lowest level the lint rule (internal/lab/bank/lint.go allowedLevels) accepts."""
    n = len(traps)
    if n == 0 and ref_calls <= 3:
        return "L0"
    if n == 1 and ref_calls <= 4:
        return "L1"
    if n == 2 or (n == 1 and (n_files >= 3 or ref_calls >= 5)):
        return "L2"
    if n >= 3 or (multi and n >= 1) or ref_calls >= 8:
        return "L3"
    raise ValueError("no level for traps=%d ref_calls=%d" % (n, ref_calls))


def is_zh(text):
    return len(re.findall(r"[一-鿿]", text)) >= 4


_VOCAB = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "workbank", "tag-vocab.json")))
TRAP_AXIS = {k: v.get("axis") for k, v in _VOCAB["traps"].items() if isinstance(v, dict)}


def case(cid, *, sub, spec, desc, task_type, family, ref_calls, files, turns, verify, notes,
         traps=(), decoys=None, axes=("OBS",), ref=None, **kw):
    """Write one case, register its behavior spec and bash reference."""
    level = level_for(traps, ref_calls, len(files), len(turns) > 1)
    axes = list(axes) + [TRAP_AXIS[t] for t in traps if TRAP_AXIS.get(t) and TRAP_AXIS[t] not in axes]
    axes = list(dict.fromkeys(axes))
    if decoys is None:
        decoys = {t: None for t in traps}
    path = BATCH.write_case(cid, desc=desc, task_type=task_type, family=family, level=level,
                            ref_calls=ref_calls, files=files, turns=turns, verify=verify, notes=notes,
                            traps=traps, decoys=decoys, axes=axes, **kw)
    SPEC[cid] = dict(spec, sub=sub)
    if ref is not None:
        REFS[cid] = (files, ref[0], ref[1])
    first = turns[0]["expect"]
    META[cid] = {"sub": sub, "lang": "zh" if is_zh(" ".join(t["prompt"] for t in turns)) else "en",
                 "turns": len(turns), "zero_first": first.get("tools") == [] and first.get("require_active_no_call", False)}
    return path


def fixture_guard(files):
    """verify.py preamble: load the case and pin the fixture, so the sabotage
    run (one number +1, or the first line deleted) always fails verify."""
    digest = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    return ("import hashlib, json\n"
            "case = json.load(open(\"case.json\"))\n"
            "_pin = hashlib.sha256(json.dumps(case[\"files\"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()\n"
            "assert _pin == %r, \"fixture changed\"\n" % digest)


def verify_src(files, body):
    return fixture_guard(files) + body.strip("\n") + "\n"


def phrasings(*items):
    assert len(items) == 5
    return "\n## Five alternative phrasings of the task\n" + "".join("%d. %s\n" % (i + 1, t) for i, t in enumerate(items))


def thousands(value):
    whole, _, frac = str(value).partition(".")
    neg = whole.startswith("-")
    grouped = ("-" if neg else "") + f"{abs(int(whole)):,}" + ("." + frac if frac else "")
    return [str(value)] if grouped == str(value) else [str(value), grouped]


_NUM = re.compile(r"-?\d+(?:\.\d+)?")


def _wordish(ch):
    return ch == "." or ch == "_" or ch.isalnum()


def number_tokens(text):
    """The numbers bank verify's sabotage scan sees (numberMatches)."""
    out = []
    for m in _NUM.finditer(text):
        if m.start() > 0 and _wordish(text[m.start() - 1]):
            continue
        if m.end() < len(text) and _wordish(text[m.end()]):
            continue
        out.append(float(m.group()))
    return out


def literal_free(files, *values):
    """No fixture number token equals any answer value (so the sabotage scan
    falls through to deleting a line rather than bumping a look-alike)."""
    nums = [n for t in files.values() for n in number_tokens(t)]
    return all(not any(abs(n - float(v)) <= 0.011 for n in nums) for v in values)


def substr_free(files, value):
    return not any(str(value) in t for t in files.values())


# ------------------------------------------------------------------ references


def run_reference(sidecar, files, commands, want):
    """Replay a reference bash solution on a scratch copy of the fixture.
    want(stdout, read) returns an error string or None; read(path) gives the
    overlay's content of path after the commands, or None when it is gone."""
    root = os.path.realpath(tempfile.mkdtemp(prefix="b14-ref-"))
    try:
        for path, content in files.items():
            target = os.path.join(root, path)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, "w", encoding="utf-8") as f:
                f.write(content)
        stdout = ""
        for command in commands:
            response = sidecar.run(root, command)
            if response.get("error") or response.get("exit_code") not in (0, 1):
                return "`%s` -> %s" % (command, response)
            stdout = response["stdout"]

        def read(path):
            sidecar.next += 1
            sidecar.proc.stdin.write(json.dumps({"id": sidecar.next, "root": root, "op": "read", "path": path}) + "\n")
            sidecar.proc.stdin.flush()
            reply = json.loads(sidecar.proc.stdout.readline())
            if reply.get("error"):
                return None
            return base64.b64decode(reply["data"]).decode("utf-8")
        return want(stdout, read)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def has(*needles):
    def check(out, _read):
        return None if all(n in out for n in needles) else "ref stdout %r lacks %s" % (out[:300], needles)
    return check


def files_check(rules, originals):
    """rules: path -> {"equals": text} | {"unchanged": True} | {"absent": True}."""
    def check(_out, read):
        for path, rule in rules.items():
            text = read(path)
            if rule.get("absent"):
                if text is not None:
                    return "%s should be gone" % path
                continue
            if text is None:
                return "%s missing" % path
            want = rule["equals"] if "equals" in rule else originals[path]
            if text != want:
                return "%s = %r" % (path, text[:300])
        return None
    return check


def rules_for(files, final):
    """expect.files rules from the fixture and the intended final tree."""
    out = {}
    for path, text in files.items():
        if path not in final:
            out[path] = {"absent": True}
        elif final[path] == text:
            out[path] = {"unchanged": True}
        else:
            out[path] = {"equals": final[path]}
    for path, text in final.items():
        if path not in files:
            out[path] = {"equals": text}
    return out

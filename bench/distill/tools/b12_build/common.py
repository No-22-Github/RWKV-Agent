"""Shared writer for the b12 pilot cases (v1.41: bash + get_weather on work-v2).

Same case layout as b10_build: bench/distill/cases/<scenario>/<id>/{case.json,
verify.py, NOTES.md}, canary derived from the case id, fixed seeds, so
re-running a builder rewrites byte-identical files.

What b12 adds over b10_build:
- weather_fixture on the case (get_weather in work-v2 answers from it);
- every bash case carries a reference command list that build.py replays in
  the real just-bash sidecar (local/bin/justbash-sidecar) before the case is
  written, so a case the sandbox cannot solve never reaches the bank.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
CASES = os.path.join(REPO, "bench", "distill", "cases")
SIDECAR = os.path.join(REPO, "local", "bin", "justbash-sidecar")
AUTHOR = "llm:claude-opus-5-5-b12"

SCEN = {"tab": "tabular", "log": "logs", "cfg": "config", "doc": "docs", "fs": "filesystem",
        "scr": "script", "code": "code", "web": "web", "hyb": "hybrid", "nt": "notool"}


def canary(cid):
    return "DISTILL-CANARY-" + hashlib.sha256(("b12-pilot:" + cid).encode()).hexdigest()[:8]


def lines(rows):
    return "".join(r + "\n" for r in rows)


def weather(city, current, days, aliases=()):
    """One weather_fixture entry; days are (date, condition, temp_c, rain_chance)
    rows starting at the work catalog's fixed today, 2026-09-16."""
    return {"location": city, "aliases": list(aliases), "report": {
        "location": city, "current": current, "source": "fixture",
        "daily": [{"date": d, "condition": c, "temp_c": t, "rain_chance": r} for d, c, t, r in days]}}


def write_case(cid, *, desc, task_type, family, level, ref_calls, files, turns, verify, notes,
               traps=(), decoys=None, axes=(), web=None, weather_fixture=None, offered_tools=None,
               case_expect=None, answer_style="natural", version=1):
    scenario = SCEN[cid.split("-")[0]]
    can = canary(cid)
    case = {
        "id": cid,
        "description": desc.rstrip(".") + ". " + can,
        "category": scenario,
        "tags": {
            "scenario": scenario,
            "task_type": task_type,
            "traps": list(traps),
            "trap_decoys": dict(decoys or {}),
            "axes": list(axes),
            "level": level,
            "family": family,
            "ref_calls": ref_calls,
            "fixture_bytes": sum(len(v.encode()) for v in files.values()),
            "status": "draft",
            "version": version,
            "author": AUTHOR,
            "reviewer": None,
            "answer_style": answer_style,
            "tool_catalog": "work-v2",
        },
        "web_fixture": list(web or []),
        "files": files,
        "turns": turns,
    }
    if weather_fixture:
        case["weather_fixture"] = list(weather_fixture)
    if offered_tools is not None:
        case["offered_tools"] = list(offered_tools)
    if case_expect:
        case["expect"] = case_expect
    d = os.path.join(CASES, scenario, cid)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "case.json"), "w") as f:
        json.dump(case, f, ensure_ascii=False, indent=2)
        f.write("\n")
    with open(os.path.join(d, "verify.py"), "w") as f:
        f.write("# %s : distillation case\n" % can)
        f.write(verify.strip("\n") + "\n")
    with open(os.path.join(d, "NOTES.md"), "w") as f:
        f.write(notes.strip("\n") + "\n")
    return d


class Sidecar:
    """Minimal client for the just-bash sidecar's JSON-lines protocol."""

    def __init__(self):
        if not os.path.exists(SIDECAR):
            sys.exit("missing %s; run scripts/build-justbash.sh" % SIDECAR)
        self.proc = subprocess.Popen([SIDECAR], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        self.next = 0

    def run(self, root, command):
        self.next += 1
        self.proc.stdin.write(json.dumps({"id": self.next, "root": root, "command": command,
                                          "timeout_ms": 20000}) + "\n")
        self.proc.stdin.flush()
        return json.loads(self.proc.stdout.readline())

    def close(self):
        self.proc.stdin.close()
        self.proc.wait()


def check_reference(sidecar, files, commands, want):
    """Replay a reference bash solution on a scratch copy of the fixture.
    want(stdout, root) returns an error string or None."""
    root = os.path.realpath(tempfile.mkdtemp(prefix="b12-ref-"))
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
        return want(stdout, root)
    finally:
        shutil.rmtree(root, ignore_errors=True)

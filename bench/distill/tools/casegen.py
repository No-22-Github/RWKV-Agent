"""Shared case writer for the batch builders (b10/, b12/, and later batches).

Each case is written as bench/distill/<version>/cases/<scenario>/<id>/
{case.json, verify.py, NOTES.md}. The canary is derived from the case id and
builders use fixed seeds, so re-running a builder rewrites byte-identical files.
A batch only differs in its Batch settings; builders import write_case from
their batch's common.py.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

from distill_paths import REPO, cases_dir

SIDECAR = os.path.join(REPO, "local", "bin", "justbash-sidecar")
SCEN = {"tab": "tabular", "log": "logs", "cfg": "config", "doc": "docs", "fs": "filesystem",
        "scr": "script", "code": "code", "web": "web", "hyb": "hybrid", "nt": "notool"}


class Batch:
    """salt seeds the canary ("b10-pilot"); tool_catalog is recorded in tags
    when the batch targets a non-default catalog (b12: "work-v2")."""

    def __init__(self, *, salt, author, version, tool_catalog=None):
        self.salt = salt
        self.author = author
        self.cases = cases_dir(version)
        self.tool_catalog = tool_catalog

    def canary(self, cid):
        return "DISTILL-CANARY-" + hashlib.sha256((self.salt + ":" + cid).encode()).hexdigest()[:8]

    def write_case(self, cid, *, desc, task_type, family, level, ref_calls, files, turns, verify, notes,
                   traps=(), decoys=None, axes=(), web=None, weather_fixture=None, offered_tools=None,
                   case_expect=None, answer_style="natural", version=1):
        scenario = SCEN[cid.split("-")[0]]
        can = self.canary(cid)
        tags = {
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
            "author": self.author,
            "reviewer": None,
            "answer_style": answer_style,
        }
        if self.tool_catalog:
            tags["tool_catalog"] = self.tool_catalog
        case = {
            "id": cid,
            "description": desc.rstrip(".") + ". " + can,
            "category": scenario,
            "tags": tags,
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
        d = os.path.join(self.cases, scenario, cid)
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


def lines(rows):
    return "".join(r + "\n" for r in rows)


def weather(city, current, days, aliases=()):
    """One weather_fixture entry; days are (date, condition, temp_c, rain_chance)
    rows starting at the work catalog's fixed today, 2026-09-16."""
    return {"location": city, "aliases": list(aliases), "report": {
        "location": city, "current": current, "source": "fixture",
        "daily": [{"date": d, "condition": c, "temp_c": t, "rain_chance": r} for d, c, t, r in days]}}


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
    root = os.path.realpath(tempfile.mkdtemp(prefix="casegen-ref-"))
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

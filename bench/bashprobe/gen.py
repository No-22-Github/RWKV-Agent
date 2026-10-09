#!/usr/bin/env python3
"""Generates the bash capability probe (bench/bashprobe/cases/*/case.json).

Every case is built from a seeded RNG, its expected answer is computed here
from the same fixture, and its reference bash solution is executed in the real
just-bash sidecar (local/bin/justbash-sidecar) before anything is written, so
a case that the sandbox cannot solve never reaches the bank.

    python3 bench/bashprobe/gen.py            # regenerate and validate
    python3 bench/bashprobe/gen.py --check    # validate only, write nothing

Run with: rwkv-cli agent-eval --cases bench/bashprobe/cases --tool-catalog work-v2
          --file-tools lines --include-draft ...
"""
import argparse
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
SIDECAR = REPO / "local" / "bin" / "justbash-sidecar"
CANARY = "BASHPROBE-CANARY-7d41c0e9"

CASES = []


def case(fn):
    CASES.append(fn)
    return fn


def lines(rows):
    return "".join(row + "\n" for row in rows)


def build(cid, *, axis, task, prompt, files, expect, ref, check, level="L0",
          traps=None, notes="", case_expect=None, turns=None, **extra):
    """Assemble one case dict plus its validation spec.

    axis   probe dimension (choice, command, aggregate, edit, recover,
           boundary, safety, closure, weather, baseline)
    ref    reference bash commands run in order inside the sidecar
    check  callable(last_stdout, workspace_path) -> error string or None
    """
    body = {
        "id": cid,
        "description": f"bash probe / {axis} / {task}. {CANARY}",
        "category": "bashprobe",
        "tags": {
            "scenario": "bashprobe",
            "task_type": task,
            "probe_axis": axis,
            "traps": traps or [],
            "level": level,
            "status": "draft",
            "version": 1,
            "author": "llm:claude-opus-5-5",
        },
        "files": files,
        "turns": turns or [{"prompt": prompt, "expect": expect}],
    }
    if case_expect:
        body["expect"] = case_expect
    body.update(extra)
    return {"case": body, "ref": ref, "check": check, "notes": notes}


class Sidecar:
    def __init__(self):
        if not SIDECAR.exists():
            sys.exit(f"missing {SIDECAR}; run scripts/build-justbash.sh")
        self.proc = subprocess.Popen([str(SIDECAR)], stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, text=True)
        self.next = 0

    def run(self, root, command):
        self.next += 1
        request = {"id": self.next, "root": str(root), "command": command, "timeout_ms": 20000}
        self.proc.stdin.write(json.dumps(request) + "\n")
        self.proc.stdin.flush()
        response = json.loads(self.proc.stdout.readline())
        if response.get("error"):
            raise RuntimeError(response["error"])
        return response

    def close(self):
        self.proc.stdin.close()
        self.proc.wait()


def validate(sidecar, spec):
    root = Path(tempfile.mkdtemp(prefix="bashprobe-"))
    try:
        for path, content in spec["case"]["files"].items():
            target = root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        stdout = ""
        for command in spec["ref"]:
            response = sidecar.run(root.resolve(), command)
            stdout = response["stdout"]
            if response["exit_code"] not in (0, 1) or "not found" in response["stderr"]:
                return f"ref `{command}` exit={response['exit_code']} stderr={response['stderr'].strip()}"
        return spec["check"](stdout, root)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    import cases_data  # noqa: F401  (registers cases through @case)
    from gen import CASES as registered  # cases_data registers on the importable module
    sidecar = Sidecar()
    failures = 0
    out = HERE / "cases"
    if not args.check:
        shutil.rmtree(out, ignore_errors=True)
    for fn in registered:
        spec = fn()
        cid = spec["case"]["id"]
        error = validate(sidecar, spec)
        status = "ok" if error is None else f"FAIL: {error}"
        print(f"{cid:10s} {spec['case']['tags']['probe_axis']:9s} {status}")
        if error is not None:
            failures += 1
            continue
        if not args.check:
            target = out / cid
            target.mkdir(parents=True, exist_ok=True)
            (target / "case.json").write_text(
                json.dumps(spec["case"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            (target / "NOTES.md").write_text(
                spec["notes"].strip() + "\n\nReference bash:\n\n" +
                "".join(f"    {c}\n" for c in spec["ref"]) +
                f"\n<!-- {CANARY} : never enters training corpora -->\n", encoding="utf-8")
    sidecar.close()
    print(f"{len(registered) - failures}/{len(registered)} cases validated")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    sys.path.insert(0, str(HERE))
    main()

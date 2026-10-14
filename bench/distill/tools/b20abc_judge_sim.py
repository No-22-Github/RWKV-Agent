#!/usr/bin/env python3
"""Offline re-score of the Qwen teacher runs (k0, k1) on b20a/b20b/b20c (20001-20140) against the current case.json.

Text criteria (output_contains / _any / _excludes, token mode) are re-evaluated from the recorded final answers; tool
criteria (forbidden / required / active no-call) from the recorded steps; runner errors and file-state failures that the
judge change does not touch are carried over from summary.json. Prints per-case old -> new status.
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
RUNS = os.path.join(ROOT, "local/runs/distill/v20/qwen")


def is_word(c):
    return c.isalpha() or c.isdigit()


def token_in(out, want):
    i = 0
    while True:
        j = out.find(want, i)
        if j < 0:
            return False
        b = out[j - 1] if j else ""
        a = out[j + len(want)] if j + len(want) < len(out) else ""
        ok = True
        if b and is_word(b) and is_word(want[0]):
            ok = False
        if j > 1 and out[j - 1] in ".," and out[j - 2].isdigit():
            ok = False
        if a and is_word(a) and is_word(want[-1]):
            ok = False
        if ok:
            return True
        i = j + 1


def turn_text_failures(e, out, tools):
    f = []
    for r in e.get("output_contains", []):
        if not (token_in(out, r) if e.get("output_contains_token") else r in out):
            f.append("missing %r" % r)
    if e.get("output_contains_any"):
        hit = any((token_in(out, a) if e.get("output_contains_any_token") else a in out) for a in e["output_contains_any"])
        if not hit:
            f.append("NOANY")
    for x in e.get("output_excludes", []):
        if x in out:
            f.append("forbidden text %r" % x)
    for t in e.get("forbidden_tools", []):
        if t in tools:
            f.append("forbidden tool %s" % t)
    for t in e.get("required_tools", []):
        if t not in tools:
            f.append("required tool %s" % t)
    return f


def main():
    cases = {}
    for p in glob.glob(os.path.join(ROOT, "bench/distill/v2.0/cases/*/*/case.json")):
        c = json.load(open(p))
        n = int(c["id"].split("-")[1]) if c["id"].split("-")[1].isdigit() else 0
        if 20001 <= n <= 20140:
            cases[c["id"]] = c
    out = {}
    for k in ("k0", "k1"):
        for rc in json.load(open(os.path.join(RUNS, "teacher-%s" % k, "summary.json")))["cases"]:
            if rc["id"] not in cases or rc["passed"]:
                continue
            c = cases[rc["id"]]
            reasons = []
            for t, ct in zip(rc["turns"], c["turns"]):
                if t.get("passed"):
                    continue
                o = t["result"]["output"]
                tools = [s.get("tool") for s in t["result"]["steps"] if s.get("action_type") == "tool"]
                f = turn_text_failures(ct["expect"], o, tools)
                # failures the judge change does not touch
                for old in t.get("failures", []):
                    if old.startswith("runner error") or old.startswith("active no-call"):
                        f.append(old[:60])
                reasons += ["T%d %s" % (t["number"], x) for x in f]
            # case-level file expectations: text of written files is rechecked, other file failures are carried over
            written = {}
            for t in rc["turns"]:
                for s in t["result"]["steps"]:
                    if s.get("tool") in ("write_file", "append_file") and isinstance(s.get("tool_arguments"), dict):
                        a = s["tool_arguments"]
                        written[a.get("path")] = written.get(a.get("path"), "") + a.get("content", "")
            for old in rc.get("failures", []):
                m = re.match(r'expect.files "(.+)" is missing required content', old)
                if m:
                    need = (c.get("expect") or {}).get("files", {}).get(m.group(1), {}).get("contains", [])
                    miss = [x for x in need if x not in written.get(m.group(1), "")]
                    if miss:
                        reasons.append("file %s lacks %s" % (m.group(1), miss))
                elif old.startswith("expect.files") or old.startswith("runner error"):
                    if not any(old in t.get("failures", []) for t in rc["turns"]):
                        reasons.append(old[:90])
            out[(rc["id"], k)] = reasons
    for (cid, k), r in sorted(out.items()):
        print("%-10s %s %s %s" % (cid, k, "STILL-FAIL" if r else "FLIPS-TO-PASS", "; ".join(r)[:300]))
    return out


if __name__ == "__main__":
    main()

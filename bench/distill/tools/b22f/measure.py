#!/usr/bin/env python3
"""Real token counts (RWKV World vocabulary, `rwkv-lab tokcount`) of every b22f fixture; not part of build.py.

    python3 measure.py [path/to/rwkv-lab]      # default: <repo>/local/bin/rwkv-lab-v3
"""
import glob
import json
import os
import subprocess
import sys
import tempfile

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
LAB = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO, "local", "bin", "rwkv-lab-v3")


def count(texts):
    with tempfile.TemporaryDirectory() as d:
        paths = []
        for i, t in enumerate(texts):
            p = os.path.join(d, "%04d.txt" % i)
            open(p, "w", encoding="utf-8").write(t)
            paths.append(p)
        out = subprocess.run([LAB, "tokcount"] + paths, capture_output=True, text=True, check=True).stdout.split("\n")
    return [int(l.split("\t")[0]) for l in out if l.strip()]


def main():
    rows = []
    for p in sorted(glob.glob(os.path.join(REPO, "bench/distill/v2.2/cases/*/*-345??/case.json"))):
        c = json.load(open(p))
        texts = [w["content"] for w in c["web_fixture"]] + list(c["files"].values())
        names = ["web:" + w["url_match"] for w in c["web_fixture"]] + ["file:" + k for k in c["files"]]
        rows.append((c["id"], c["tags"]["subtype"], names, count(texts) if texts else []))
    print("id\tsub\ttotal_tokens\tparts")
    for cid, sub, names, cnt in rows:
        print("%s\t%s\t%d\t%s" % (cid, sub, sum(cnt), " ".join("%s=%d" % (n.split("/")[-1][:24], k) for n, k in zip(names, cnt))))
    for sub in ("F1", "F2", "F3", "F4"):
        v = sorted(sum(r[3]) for r in rows if r[1] == sub)
        print("%s n=%d min=%d median=%d max=%d" % (sub, len(v), v[0], v[len(v) // 2], v[-1]))


if __name__ == "__main__":
    main()

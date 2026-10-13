#!/usr/bin/env python3
"""8-character fragment overlap between the b14 prompts and every reference bank.

    python3 bench/distill/tools/b14/dedup.py [--threshold 0.3] [--json out.json]

A case's text is all of its turn prompts joined, lowercased, with whitespace
and punctuation removed (letters, digits and CJK kept). Its fragments are the
set of 8-character windows (a text shorter than 8 is one fragment).
score(new, ref) = |F(new) & F(ref)| / |F(new)|, the share of the new prompt
that appears in the reference; the report gives, for every new case, its
highest score against each bank and the reference id that produced it.

Reference banks are read here by program only, never by hand: their prompt
text is not printed, only ids and scores (bashprobe / weatherprobe / workbank
are test sets).
"""
import argparse
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from distill_paths import DISTILL, REPO  # noqa: E402

NEW = os.path.join(DISTILL, "v1.42", "cases")
BANKS = {
    "distill": [p for p in glob.glob(os.path.join(DISTILL, "v*", "cases")) if not p.startswith(NEW)] +
               glob.glob(os.path.join(DISTILL, "v*", "cases-shelved")),
    "bashprobe": [os.path.join(REPO, "bench", "bashprobe", "cases")],
    "weatherprobe": [os.path.join(REPO, "bench", "weatherprobe", "cases")],
    "workbank": glob.glob(os.path.join(REPO, "bench", "workbank", "cases*")),
}
KEEP = re.compile(r"[0-9a-z㐀-鿿]")


def norm(text):
    return "".join(ch for ch in text.lower() if KEEP.match(ch))


def frags(text, n=8):
    t = norm(text)
    if len(t) <= n:
        return {t} if t else set()
    return {t[i:i + n] for i in range(len(t) - n + 1)}


def prompts(path):
    try:
        with open(path, encoding="utf-8") as f:
            case = json.load(f)
    except (OSError, ValueError):
        return None, None
    turns = case.get("turns") or []
    return case.get("id") or os.path.basename(os.path.dirname(path)), "\n".join(t.get("prompt", "") for t in turns if isinstance(t, dict))


def load(roots):
    out = []
    for root in roots:
        for path in glob.glob(os.path.join(root, "**", "case.json"), recursive=True):
            cid, text = prompts(path)
            if cid:
                out.append((cid, frags(text)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--threshold", type=float, default=0.3)
    ap.add_argument("--json")
    args = ap.parse_args()
    new = load([NEW])
    banks = {name: load(roots) for name, roots in BANKS.items()}
    # inverted index per bank: fragment -> ref indices
    rows = []
    for name, refs in banks.items():
        index = {}
        for k, (_, fs) in enumerate(refs):
            for g in fs:
                index.setdefault(g, []).append(k)
        for cid, fs in new:
            hits = {}
            for g in fs:
                for k in index.get(g, ()):
                    hits[k] = hits.get(k, 0) + 1
            best = max(hits.items(), key=lambda kv: kv[1], default=(None, 0))
            score = best[1] / len(fs) if fs else 0.0
            rows.append({"case": cid, "bank": name, "score": round(score, 3), "ref": refs[best[0]][0] if best[0] is not None else None})
    by_bank = {}
    for r in rows:
        b = by_bank.setdefault(r["bank"], {"refs": len(banks[r["bank"]]), "max": 0.0, "max_case": None, "max_ref": None, "over": []})
        if r["score"] > b["max"]:
            b.update(max=r["score"], max_case=r["case"], max_ref=r["ref"])
        if r["score"] > args.threshold:
            b["over"].append(r)
    print("new cases: %d; fragment size 8; threshold %.2f" % (len(new), args.threshold))
    for name, b in by_bank.items():
        print("%-12s refs %5d  max %.3f (%s vs %s)  over threshold: %d" % (name, b["refs"], b["max"], b["max_case"], b["max_ref"], len(b["over"])))
        for r in sorted(b["over"], key=lambda r: -r["score"]):
            print("    %-11s %.3f  %s" % (r["case"], r["score"], r["ref"]))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump({"banks": by_bank, "rows": rows}, f, ensure_ascii=False, indent=1)
            f.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

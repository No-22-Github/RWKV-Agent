#!/usr/bin/env python3
"""dedup.py — surface-similarity marking for workbank cases within one scenario.

For every pair of cases with the same tags.scenario:
  - prompt similarity: word 3-gram Jaccard over the prompts with the global
    answer contract stripped; flag when > 0.6
  - fixture similarity: Jaccard over the sets of all numbers appearing in the
    case's files contents; flag when > 0.5

Output: a JSON array of {"case_a", "case_b", "prompt_jaccard", "numbers_jaccard"}
for the marked pairs on stdout (empty array when clean) plus a WARNING line on
stderr. Exit code is always 0 — dedup marks, a human decides.
Standard library only.
"""

import argparse
import json
import re
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
WORKBANK_DIR = TOOLS_DIR.parent
DEFAULT_CASES = WORKBANK_DIR / "cases"
DEFAULT_VOCAB = WORKBANK_DIR / "docs" / "tag-vocab.json"

PROMPT_JACCARD_THRESHOLD = 0.6
NUMBERS_JACCARD_THRESHOLD = 0.5
WORD_RE = re.compile(r"[a-z0-9]+")
NUMBER_RE = re.compile(r"-?\d+(?:,\d{3})*(?:\.\d+)?")


def load_contracts(vocab_path):
    with open(vocab_path, encoding="utf-8") as fh:
        vocab = json.load(fh)
    return list(vocab["answer_contracts"].values())


def strip_contracts(text, contracts):
    for contract in contracts:
        idx = text.rfind(contract)
        if idx != -1:
            text = text[:idx]
    return text.strip()


def word_ngrams(text, n=3):
    words = WORD_RE.findall(text.lower())
    return {" ".join(words[i:i + n]) for i in range(len(words) - n + 1)}


def numbers_of_case(case):
    numbers = set()
    for content in (case.get("files") or {}).values():
        for raw in NUMBER_RE.findall(content):
            numbers.add(float(raw.replace(",", "")))
    return numbers


def jaccard(set_a, set_b):
    union = set_a | set_b
    return len(set_a & set_b) / len(union) if union else 0.0


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Mark near-duplicate workbank case pairs within the same scenario "
                    "(prompt 3-gram Jaccard > 0.6 or fixture number-set Jaccard > 0.5).")
    parser.add_argument("--cases", default=str(DEFAULT_CASES),
                        help=f"cases root directory (default: {DEFAULT_CASES})")
    parser.add_argument("--vocab", default=str(DEFAULT_VOCAB),
                        help=f"tag vocabulary file (default: {DEFAULT_VOCAB})")
    args = parser.parse_args(argv)

    contracts = load_contracts(args.vocab)
    cases = []
    for path in sorted(Path(args.cases).rglob("case.json")):
        try:
            with open(path, encoding="utf-8") as fh:
                case = json.load(fh)
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        tags = case.get("tags") or {}
        scenario = tags.get("scenario")
        if not isinstance(scenario, str):
            continue
        prompts = " ".join(
            strip_contracts(t.get("prompt") or "", contracts)
            for t in case.get("turns") or [] if isinstance(t, dict))
        cases.append({
            "id": case.get("id") or path.parent.name,
            "scenario": scenario,
            "ngrams": word_ngrams(prompts),
            "numbers": numbers_of_case(case),
        })

    marked = []
    for i, a in enumerate(cases):
        for b in cases[i + 1:]:
            if a["scenario"] != b["scenario"]:
                continue
            prompt_j = jaccard(a["ngrams"], b["ngrams"])
            numbers_j = jaccard(a["numbers"], b["numbers"])
            if prompt_j > PROMPT_JACCARD_THRESHOLD or numbers_j > NUMBERS_JACCARD_THRESHOLD:
                marked.append({
                    "case_a": a["id"],
                    "case_b": b["id"],
                    "prompt_jaccard": round(prompt_j, 4),
                    "numbers_jaccard": round(numbers_j, 4),
                })

    print(json.dumps(marked, ensure_ascii=False, indent=2))
    if marked:
        print(f"WARNING: {len(marked)} pair(s) flagged as near-duplicates; needs human confirmation",
              file=sys.stderr)
    else:
        print("no near-duplicate pairs flagged", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

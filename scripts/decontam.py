#!/usr/bin/env python3
"""Flag distillation cases that are too close to the test bank.

The workbank canary strings live only in descriptions and verify scripts,
never in model-visible text, so a derived variant (same files, renamed
numbers, reworded prompt) carries no canary. This gate compares what the
model sees instead: the prompt and the fixture files.

    python3 scripts/decontam.py --test bench/workbank/cases --candidates bench/distill/cases
    python3 scripts/decontam.py --test bench/workbank/cases \
        --records datasets/workspace-agent-700-20260920/generated/normalized/all.jsonl

For each candidate it reports the nearest test case and three scores:

- prompt:  Jaccard of word 5-gram shingles of the task prompt;
- files:   share of the candidate's fixture shingles (line 3-grams) found in
           the nearest test case's fixtures (containment, so a test fixture
           reused inside a larger candidate workspace still counts);
- names:   Jaccard of distinctive identifiers (hyphenated or dotted names such
           as notify-hub, CHG-2193, ledger_sync.yaml) across prompt and files.

Shingles and names present in more than --boilerplate of the test cases
(answer-contract sentences, README.md-style names) are ignored on both sides,
so shared templates do not read as shared tasks.

A candidate is flagged when any score reaches its threshold. Exit status 1
when anything is flagged, so the gate can stop a pipeline.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

WORD = re.compile(r"[a-z0-9]+")
NAME = re.compile(r"\b[A-Za-z][A-Za-z0-9]*(?:[-_.][A-Za-z0-9]+)+\b")
# Too common across any workspace task to count as a shared identity.
COMMON_NAMES = {"readme.md", "e.g", "i.e"}


def load_bank(root: Path) -> list[dict]:
    return [json.loads(path.read_text(encoding="utf-8")) for path in sorted(root.rglob("case.json"))]


def load_records(path: Path) -> list[dict]:
    cases = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            record = json.loads(line)
            cases.append({"id": record["id"], "files": record.get("initial_files") or {},
                          "turns": [{"prompt": record["task"]}]})
    return cases


def prompt_of(case: dict) -> str:
    return "\n".join(turn.get("prompt", "") for turn in case.get("turns", []))


def word_shingles(text: str, size: int = 5) -> set:
    words = WORD.findall(text.lower())
    return {tuple(words[i:i + size]) for i in range(max(0, len(words) - size + 1))}


def line_shingles(files: dict, size: int = 3) -> set:
    shingles = set()
    for content in files.values():
        lines = [line.strip() for line in str(content).splitlines() if line.strip()]
        shingles.update(tuple(lines[i:i + size]) for i in range(max(0, len(lines) - size + 1)))
        if 0 < len(lines) < size:
            shingles.add(tuple(lines))
    return shingles


def names(case: dict) -> set:
    text = prompt_of(case) + "\n" + "\n".join(str(v) for v in (case.get("files") or {}).values())
    text += "\n" + "\n".join(case.get("files") or {})
    return {name.lower() for name in NAME.findall(text)} - COMMON_NAMES


def jaccard(left: set, right: set) -> float:
    return len(left & right) / len(left | right) if left and right else 0.0


def containment(part: set, whole: set) -> float:
    return len(part & whole) / len(part) if part else 0.0


def features(case: dict) -> dict:
    return {"prompt": word_shingles(prompt_of(case)), "files": line_shingles(case.get("files") or {}),
            "names": names(case)}


def boilerplate(all_features: list[dict], share: float) -> dict:
    """Features present in more than share of the test cases, per kind."""
    common = {}
    for kind in ("prompt", "files", "names"):
        counts = {}
        for item in all_features:
            for feature in item[kind]:
                counts[feature] = counts.get(feature, 0) + 1
        limit = share * len(all_features)
        common[kind] = {feature for feature, count in counts.items() if count > limit}
    return common


def strip(item: dict, common: dict) -> dict:
    return {kind: item[kind] - common[kind] for kind in item}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--test", type=Path, required=True, help="test bank directory (case.json files)")
    parser.add_argument("--candidates", type=Path, help="candidate bank directory")
    parser.add_argument("--records", type=Path, help="or: normalized records JSONL")
    parser.add_argument("--prompt-threshold", type=float, default=0.35)
    parser.add_argument("--files-threshold", type=float, default=0.30)
    parser.add_argument("--names-threshold", type=float, default=0.30)
    parser.add_argument("--boilerplate", type=float, default=0.05,
                        help="ignore features present in more than this share of test cases")
    parser.add_argument("--report", type=Path, help="optional JSONL with every candidate's scores")
    args = parser.parse_args()
    if bool(args.candidates) == bool(args.records):
        parser.error("give exactly one of --candidates or --records")

    test = [(case["id"], features(case)) for case in load_bank(args.test)]
    common = boilerplate([f for _, f in test], args.boilerplate)
    test = [(case_id, strip(f, common)) for case_id, f in test]
    candidates = load_bank(args.candidates) if args.candidates else load_records(args.records)
    thresholds = {"prompt": args.prompt_threshold, "files": args.files_threshold, "names": args.names_threshold}
    rows, flagged = [], []
    for case in candidates:
        mine = strip(features(case), common)
        best = {"prompt": (0.0, ""), "files": (0.0, ""), "names": (0.0, "")}
        for test_id, theirs in test:
            scores = {"prompt": jaccard(mine["prompt"], theirs["prompt"]),
                      "files": containment(mine["files"], theirs["files"]),
                      "names": jaccard(mine["names"], theirs["names"])}
            for key, value in scores.items():
                if value > best[key][0]:
                    best[key] = (value, test_id)
        hits = [key for key in thresholds if best[key][0] >= thresholds[key]]
        row = {"id": case["id"], **{key: round(value, 3) for key, (value, _) in best.items()},
               "nearest": {key: test_id for key, (_, test_id) in best.items()}, "flagged": hits}
        rows.append(row)
        if hits:
            flagged.append(row)

    if args.report:
        with args.report.open("x", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"decontam: {len(candidates)} candidates vs {len(test)} test cases; {len(flagged)} flagged")
    for key in thresholds:
        print(f"  {key:6s} >= {thresholds[key]:.2f}: {sum(key in row['flagged'] for row in rows)}")
    for row in flagged[:15]:
        nearest = row["nearest"][row["flagged"][0]]
        print(f"  {row['id']}  prompt {row['prompt']:.2f}  files {row['files']:.2f}  names {row['names']:.2f}  ~ {nearest}")
    if len(flagged) > 15:
        print(f"  … {len(flagged) - 15} more")
    return 1 if flagged else 0


if __name__ == "__main__":
    sys.exit(main())

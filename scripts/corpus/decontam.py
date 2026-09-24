"""Flag distillation cases that are too close to the test bank.

The workbank canary strings live only in descriptions and verify scripts,
never in model-visible text, so a derived variant (same files, renamed
numbers, reworded prompt) carries no canary. This gate compares what the
model sees instead (see similarity.py for the features):

    python3 -m scripts.corpus decontam --test bench/workbank/cases --candidates bench/distill/cases
    python3 -m scripts.corpus decontam --test bench/workbank/cases \\
        --records datasets/workspace-agent-700-20260920/generated/normalized/all.jsonl

For each candidate it reports the nearest test case per score. Features
present in more than --boilerplate of the test cases (answer-contract
sentences, README.md-style names) are ignored on both sides, so shared
templates do not read as shared tasks. A candidate is flagged when any score
reaches its threshold; the exit status is 1 when anything is flagged, so the
gate can stop a pipeline.
"""

from __future__ import annotations

from pathlib import Path

from . import bank, jsonl, similarity
from .similarity import KINDS


def add_arguments(parser) -> None:
    parser.add_argument("--test", type=Path, required=True, help="test bank directory (case.json files)")
    parser.add_argument("--candidates", type=Path, help="candidate bank directory")
    parser.add_argument("--records", type=Path, help="or: normalized records JSONL")
    parser.add_argument("--prompt-threshold", type=float, default=0.35)
    parser.add_argument("--files-threshold", type=float, default=0.30)
    parser.add_argument("--names-threshold", type=float, default=0.30)
    parser.add_argument("--boilerplate", type=float, default=0.05,
                        help="ignore features present in more than this share of test cases")
    parser.add_argument("--report", type=Path, help="optional JSONL with every candidate's scores")


def run(args) -> int:
    if bool(args.candidates) == bool(args.records):
        args.error("give exactly one of --candidates or --records")
    thresholds = {"prompt": args.prompt_threshold, "files": args.files_threshold, "names": args.names_threshold}
    test = [(case["id"], similarity.features(case)) for case in bank.load(args.test)]
    common = similarity.boilerplate([features for _, features in test], args.boilerplate)
    test = [(case_id, similarity.strip(features, common)) for case_id, features in test]
    if args.candidates:
        candidates = bank.load(args.candidates)
    else:
        candidates = [bank.record_to_case(record) for record in jsonl.read(args.records)]

    rows = [nearest(case, test, common, thresholds) for case in candidates]
    if args.report:
        jsonl.write(args.report, rows)
    flagged = [row for row in rows if row["flagged"]]
    print(f"decontam: {len(candidates)} candidates vs {len(test)} test cases; {len(flagged)} flagged")
    for kind in KINDS:
        print(f"  {kind:6s} >= {thresholds[kind]:.2f}: {sum(kind in row['flagged'] for row in rows)}")
    for row in flagged[:15]:
        closest = row["nearest"][row["flagged"][0]]
        print(f"  {row['id']}  prompt {row['prompt']:.2f}  files {row['files']:.2f}  names {row['names']:.2f}  ~ {closest}")
    if len(flagged) > 15:
        print(f"  … {len(flagged) - 15} more")
    return 1 if flagged else 0


def nearest(case: dict, test: list[tuple[str, dict]], common: dict, thresholds: dict[str, float]) -> dict:
    """Best score per kind over the test bank (first test case wins ties)."""
    mine = similarity.strip(similarity.features(case), common)
    best = {kind: (0.0, "") for kind in KINDS}
    for test_id, theirs in test:
        for kind, value in similarity.scores(mine, theirs).items():
            if value > best[kind][0]:
                best[kind] = (value, test_id)
    return {"id": case["id"], **{kind: round(value, 3) for kind, (value, _) in best.items()},
            "nearest": {kind: test_id for kind, (_, test_id) in best.items()},
            "flagged": [kind for kind in KINDS if best[kind][0] >= thresholds[kind]]}

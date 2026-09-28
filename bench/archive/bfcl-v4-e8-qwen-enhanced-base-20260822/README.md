# BFCL v4 E8 Qwen enhanced base archive

This directory freezes the compact, reviewable evidence for the Qwen3-8B-FP8
enhanced `multi_turn_base` run scored on 2026-08-22.

- Official partial-evaluation score: **57/200 (28.50%)**
- Dataset commit: `6ea57973c7a6097fd7c5915698c54c17c5b1b6c8`
- Evaluator: `bfcl-eval==2026.3.23`
- Generation source commit: `2fba06dfc271b4abc41fe3e6adbcdd00ea990628`
- Generation binary SHA-256: `aaf77d95ebffd43d6760eb9607c243de179c1b8b90d2d255d1a5f7e93bed9ba0`

Files:

- `result.jsonl`: all 200 merged model results accepted by the evaluator.
- `archive.json`: frozen run configuration, aggregate Harness metrics, event/exit
  counts, official score summary, and hashes of every local score artifact.
- `official-score-summary.json`: compact public score and failure distribution.
- `data_multi_turn.csv`: evaluator-produced section table. Use its Base column;
  the Multi Turn Overall column includes three unrun splits in its denominator.

The evaluator's full 800 KiB failure-detail JSONL remains in the ignored local
run because it duplicates BFCL prompts, initial state, ground truth and synthetic
credentials. Its SHA-256 is frozen in the compact summary and `archive.json`.

The interpretation and reproduction commands are in
`docs/evaluations/bfcl-v4-e8-qwen-enhanced-base-20260822.md`.

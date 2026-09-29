# Archived: workspace-agent-700 standard export set (2026-09-20)

Frozen copy of the standard export of the **700-record agent corpus**
(`phase3-repaired-700-20260920`; 630 train + 70 validation; acceptance verdict
`data_ready`).

Archived for two reasons, per the `bench/README.md` rules:

1. These are paid-for teacher trajectories — the sampling behind them is not
   reproducible, so they count as source data, not derived artifacts.
2. `generated/normalized/all.jsonl` is the *only* dependency that
   `bench/distill/scripts/base700.jsonl` lacks for in-repo re-rendering. With
   it committed, the base700 reproducibility chain closes inside the repo.

## Contents (20 files)

- `generated/normalized/{all,train,validation}.jsonl` — 700 full normalized
  records: task, tool trajectory, real tool receipts, acceptance metadata.
- `generated/rendered/none-ctx4096/{train,validation}.jsonl` — actual training
  text with `loss_spans` and meta (630 / 70).
- `generated/hashes.json`, `generated/split-manifest.json`,
  `generated/README.md` — record/render/grouping evidence and export notes.
- `verification/` (9 files) — acceptance report, phase-3 repair reports and
  ledgers, export-integrity check, retention policy.
- `ACCEPTANCE.md`, `TASKORDER-700.md` — acceptance criteria and production
  spec. `SHA256SUMS.json` — sha256 of every file in this directory.

Training input uses the `rendered` files and follows `loss_spans`; the
normalized records carry acceptance-side fields and must not be concatenated
into model input as-is. Max tokenizer length is 3352 (cap 4096).

## Honest caveats (mirrored from ACCEPTANCE.md)

- "700" counts records, not structurally independent tasks: 13 near-duplicate
  train records are retained by explicit user authorization — see
  `verification/phase3-retention-policy.json`.
- 682 records passed independent review; the other 18 were retained through
  production-side repair or the same user authorization.

## Provenance and integrity

- Self-produced fictional workspace-scenario corpus (ws700 production run,
  frozen 2026-09-20). No third-party dataset or upstream license involved;
  cleared for publication in this public repository as of 2026-09-29.
- Every file is byte-identical to `local/outputs/workspace-agent-700/` and to
  the `generated/` + `verification/` subtrees of the making workspace
  `local/datasets/workspace-agent-700-20260920/`; verified against
  `SHA256SUMS.json` at archive time (20/20 OK).
- The making workspace itself (records / sessions / sketches / seeds /
  tooling, ~77 MB of process artifacts) stays out of the repo by design. Both
  remaining copies are local-only:
  - full-workspace backup `local/datasets/workspace-agent-700-20260920.zip`
    (10 895 files), sha256 `c675f2843feee3a7107d8c0778256b14cc5c259e28eb7e043598889134c4b35f`;
  - export zip `local/outputs/workspace-agent-700-export-20260920.zip`,
    sha256 `85d1eae1100b47294a4a56b53fa160a6c777fac91baccdd0dfbdf77f962c4e37`.

## Re-rendering base700

```sh
local/bin/rwkv-lab corpus render \
  --records bench/archive/workspace-agent-700-20260920/generated/normalized/all.jsonl \
  --source base700 --out local/runs/distill/base700-rebuilt
```

All rows rendered for one pack must come from the same `rwkv-cli` build
(`wire_hash` changes with the harness); see
[`bench/distill/scripts/README.md`](../../distill/scripts/README.md) for the
current hash and the full procedure.

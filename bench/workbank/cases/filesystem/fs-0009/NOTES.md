## Traps
- none: L0 baseline of fam-fs-dedupe-03 (duplicates/presence skeleton, presence side). The question names one artifact, exactly one file in the workspace matches it, and no decoy or near-name is planted.

## Reference solution
1. list_files the workspace and collect the entries under telemetry/ (call 1)
2. read telemetry/gateway.yaml and confirm it opens with the `gateway:` block the README describes (call 2)
3. answer telemetry/gateway.yaml (call 3)

## Why the answer is unique
telemetry/ holds a single YAML definition, and it is the only file anywhere whose first line opens the `gateway:` block; notes/handover-journal.md is prose and README.md is documentation. The workspace path telemetry/gateway.yaml is therefore the only candidate. verify.py recomputes the path by scanning the fixture for a telemetry/ file whose first line is `gateway:`, so the answer is derived from the bytes, not stated.

<!-- WORKBANK-CANARY-4b7c1e92 : this file must never enter training corpora -->

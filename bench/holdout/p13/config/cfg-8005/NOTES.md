# cfg-8005 (p13 holdout, eval-only)

## Traps
- TR-DECOY: `interval_minutes` appears twice, once per section. 正式环境 is the `[sync]` section (its endpoint has no `.staging.` infix); the `[staging]` value 10 must stay. Editing the staging value, changing both, or inserting a new line instead of replacing the 30 line all fail the needles. `trap_decoys` is null: the wrong outcome is a file state, not a single value.

## Reference solution
1. Read config/sync.conf (ref call 1).
2. Replace the `interval_minutes = 30` line in the `[sync]` section with `interval_minutes = 15`, leaving every other line as it is (ref call 2).

## Why the answer is unique
Three substrings are scored. The first spans the file's very first line through the new 15 value, so deleting or inserting lines anywhere in that span (including prepending or adding rather than replacing) breaks it. The second spans the new value into the following `batch` line, so surrounding lines must survive. The third is the whole `[staging]` block, so the staging interval must stay 10. Only the single-line edit inside `[sync]` satisfies all three, and any rewrite that reorders or rewraps lines breaks them, so the end state is unique.

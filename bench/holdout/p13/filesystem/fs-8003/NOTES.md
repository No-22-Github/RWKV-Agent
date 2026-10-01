# fs-8003 (p13 holdout, eval-only)

## Traps
- TR-DECOY: two receipt rows (QW-30860, QW-30913) are amount-0 placeholders registered by the cashier, and finance/README.md says they do not count as received. Treating them as receipts leaves only QW-30825 in the report; listing every order without checking receipts produces a superset. Either way the contiguous three-line ascending block needle fails. `trap_decoys` is null: the wrong outcome is a file state, not a single value.

## Reference solution
1. Read finance/README.md for the placeholder rule (ref call 1).
2. Read finance/orders-2026-09.csv for the order IDs (ref call 2).
3. Read finance/receipts-2026-09.csv, skipping the two amount-0 占位 rows (ref call 3).
4. Write reports/unreceipted-2026-09.txt with QW-30825, QW-30860, QW-30913 - one per line, ascending (ref call 4).

## Why the answer is unique
Four orders have valid receipts (QW-30790, QW-30841, QW-30897, QW-30931); the remaining three are exactly QW-30825, QW-30860 and QW-30913, and the prompt fixes one per line ascending, so the report is that three-line block. The decoy rows sort between the real missing IDs (30860 and 30913 sit inside the 30825..30913 span), so a superset breaks the block's contiguity and fails. The three source files are pinned byte-for-byte by `equals`.

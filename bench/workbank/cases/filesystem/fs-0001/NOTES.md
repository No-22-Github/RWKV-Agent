## Traps
- none: L0 baseline of fam-fs-inventory-01 (inventory/location skeleton). No decoys, no name games; every file is ordinary prose or plain CSV.

## Reference solution
1. list_files over the workspace root (default depth covers all three levels) and read each file entry's size in bytes (call 1)
2. take the maximum: exports/chain_wide_totals_2026-08.csv is the largest at 497 bytes; answer 497 (call 2)

## Why the answer is unique
Exactly one file is largest: the chain-wide totals CSV (497 bytes) outweighs the next largest, the weekly extract (341 bytes), by 156 bytes, and the README (280) and memos (221, 220) are smaller still. The empty archive placeholder can never be the maximum. Sizes are on-disk byte counts as reported by the workspace listing.

<!-- WORKBANK-CANARY-3e7a19c4 : this file must never enter training corpora -->

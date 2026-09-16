## Traps
- none: L0 baseline of fam-fs-inventory-01 (inventory/location skeleton). No decoys, no name games; every file is ordinary prose or plain CSV.

## Reference solution
1. list_files over the workspace root (default depth covers all three levels) and read each file entry's size in bytes (call 1)
2. take the maximum: exports/chain_wide_totals_2026-08.csv is the largest, answer its byte count (call 2)

## Why the answer is unique
Exactly one file is largest: the chain-wide totals CSV outweighs the weekly extract by several hundred bytes, and the README and memos are far smaller. The empty archive placeholder can never be the maximum. Sizes are on-disk byte counts as reported by the workspace listing.

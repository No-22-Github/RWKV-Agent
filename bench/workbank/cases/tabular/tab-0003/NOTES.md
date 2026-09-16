## Traps
- TR-DUPROW: the export contains byte-identical re-exported rows -
  TC-3074 appears three times, TC-3091 and TC-3138 twice each - so the
  file has 23 data rows but only 19 orders. Counting rows instead of
  orders gives the decoy 23.

## Reference solution
1. read_file README.md - the export has one row per order (1)
2. read_file orders_march.csv - 23 data rows, several of them exact
   repeats of an earlier row (2)
3. collapse repeated rows onto their order_id and count the distinct
   values: 19 (3)

## Why the answer is unique
The README fixes the grain of the file (one row per order), so a repeated
row can only be the same order written again, not a second line item.
Every repeated row is byte-identical down to order_id and qty, so no
split-by-quantity or partial-repeat reading exists, and the question asks
for orders rather than rows.

<!-- WORKBANK-CANARY-2a68d3c7 : this file must never enter training corpora -->

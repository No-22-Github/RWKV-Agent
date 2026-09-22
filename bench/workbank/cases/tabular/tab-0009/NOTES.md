# tab-0009 - Trellis Park handheld count under shelf minimum

## Traps
- None. This is the plain base case of the inventory family: one export,
  one numeric condition, one integer answer.

## Reference solution
1. read_file stocktake_2026-09-15.csv - thirteen counted lines with
   on_hand and safety_stock (1)
2. read_file README.md - a line is short when on_hand is below the shelf
   minimum (2)
3. compare the two columns line by line; the short lines are BWO-1140,
   BWO-1203, BWO-1355, BWO-1402, BWO-1428, BWO-1533 and BWO-1657, so the
   count is 7 (3)

## Why the answer is unique
The comparison is strict (`below`), and no counted line sits exactly at
its minimum, so reading the boundary as inclusive changes nothing: the
count is 7 either way. The closest calls fall clear on both sides -
BWO-1310 holds 26 against a minimum of 25 and is not short, BWO-1657
holds 33 against 35 and is. The file has one row per SKU and no row is
repeated, so exactly 7 lines fall under their minimum.

<!-- WORKBANK-CANARY-4f7c1a92 : this file must never enter training corpora -->

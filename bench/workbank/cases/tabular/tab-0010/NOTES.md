# tab-0010 - Kestrelmed ward stock below reorder point

## Traps
- TR-DELIM: the scanner export is held in one column layout and the
  replenishment plan in another; in the plan two item fields are wrapped
  in quotes because the item text itself contains a comma
  ("Nitrile gloves, medium", "Adhesive strip, waterproof"). Splitting the
  plan lines naively on commas pushes those two rows out of alignment, so
  the reorder point column reads the tail of the item text instead of a
  number and both rows drop out of the comparison. Both KMD-2073 and
  KMD-2205 are below their point in the real data, so the misread loses
  two hits: 6 becomes 4, the registered decoy.

## Reference solution
1. read_file stock_scan.tsv - ten catalogue numbers with the units
   counted on the shelf, one per line (1)
2. read_file replenishment_plan.csv - the reorder point for each of the
   same catalogue numbers, with two item fields wrapped because they
   contain a comma (2)
3. read_file README.md - a catalogue number needs a top-up when units on
   hand are below its reorder point (3)
4. match the two lists and count: KMD-2073, KMD-2140, KMD-2205,
   KMD-2249, KMD-2378 and KMD-2411 are below, so the answer is 6 (4)

## Why the answer is unique
The two files share one catalogue key and each of the ten keys appears in
both, so the comparison is well defined line by line. No row sits exactly at its
reorder point, so reading the boundary as inclusive changes nothing and
the count is 6 either way. The near misses are clear of it on both sides:
KMD-2186 holds 31 against a point of 25 and KMD-2290 holds 63 against 55,
neither below; KMD-2411 holds 12 against 20 and is. Exactly 6 rows are
below.

<!-- WORKBANK-CANARY-8d3e6b05 : this file must never enter training corpora -->

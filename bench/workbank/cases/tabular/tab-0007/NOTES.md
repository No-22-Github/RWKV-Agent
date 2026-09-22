<!-- WORKBANK-CANARY-7e15c8d4 : this file must never enter training corpora -->

## Traps
- TR-MISSING: the hours column of pick_log_june_2026.csv mixes three
  notations for an unrecorded figure - an empty cell (HG-5512, HG-5541),
  NA (HG-5529, HG-5562) and "-" (HG-5508, HG-5560) - alongside real decimal
  figures. Aggregating the raw column errors out, and a hand recompute that
  keeps those three Picking rows in the denominator divides by all eight
  Picking workers: 801.0 / 8 = 100.125 (registered decoy) instead of
  801.0 / 5 = 160.2.

## Reference solution
1. read README.md - the monthly department figure is the average hours per
   worker over the workers who have an hours figure for the month (1)
2. read employee_roster.csv - the Picking department is HG-5512, HG-5521,
   HG-5529, HG-5534, HG-5547, HG-5553, HG-5560 and HG-5568 (2)
3. read pick_log_june_2026.csv - of those, three carry no figure; the five
   figures are 168.5, 152.25, 174.0, 145.75 and 160.5 (3)
4. calculate 801.0 / 5 = 160.2 (4)

## Why the answer is unique
The README fixes the denominator as the workers of the department who have an
hours figure for the month, so the three notations for an unrecorded figure
are excluded from the count as well as from the total. That leaves five
Picking figures summing to 801.0, and 160.2 is the only average. The decoy
100.125 comes from counting the three figureless rows in the denominator, a
reading the README's stated basis rules out; the remaining Picking worker
totals (801.0 itself, or a per-unit figure) answer a different question.

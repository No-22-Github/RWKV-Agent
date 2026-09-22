# tab-0012 - Rivermouth Sable Terminal stock below reorder point

## Traps
- TR-DELIM: the count feed is held in one column layout and the reorder
  plan in another; two item fields in the plan are wrapped in quotes
  because the item text itself contains a comma ("Tarpaulin, heavy duty",
  "Shrink film, 500mm"). Splitting the plan lines naively on commas
  pushes those rows out of alignment, so the reorder point column reads
  the tail of the item text instead of a number. RF-6104 is below its
  point in the real data and drops out of the misread, taking 275.50 with
  it: 5115.8 becomes 4840.30, the registered decoy for this trap.
- TR-DUPROW: the count feed carries four whole lines that are exact
  repeats of an earlier line (RF-6172, RF-6208, RF-6317 and RF-6468). The
  README fixes the grain - one line per item held at the terminal - so a
  repeated line is the same item written again. Two of the repeated items
  are below their point, so treating every line as its own item adds
  546.00 (RF-6172) and 902.00 (RF-6208) on top of the true value:
  5115.8 becomes 6563.80, the registered decoy for this trap.

## Reference solution
1. read_file README.md - one line per item, below point means counted
   units under the reorder point, value is units times standard cost (1)
2. read_file stock_scan.tsv - eleven items with their counted units, plus
   four repeated lines for RF-6172, RF-6208, RF-6317 and RF-6468 (2)
3. read_file reorder_plan.csv - the reorder point per catalogue number,
   with two item fields wrapped because they contain a comma (3)
4. read_file unit_costs.csv - the standard cost per catalogue number (4)
5. calculator - the items below their point are RF-6104, RF-6172,
   RF-6208, RF-6281, RF-6352 and RF-6424; value each at its counted units
   times its standard cost and add: 275.50 + 546.00 + 902.00 + 627.20 +
   499.70 + 2265.40 = 5115.8 (5)

## Why the answer is unique
The README fixes the grain of the feed (one line per item), so the four
repeated lines cannot be four further items, and it fixes the boundary
(strictly below the reorder point), so the near misses RF-6139 at 52
against 45, RF-6245 at 141 against 120, RF-6317 at 430 against 400,
RF-6390 at 162 against 150 and RF-6468 at 520 against 500 all stay out.
Each catalogue number appears once in the plan and once in the cost list,
so each surviving item has exactly one value and the total is 5115.8.

<!-- WORKBANK-CANARY-6b0f8d34 : this file must never enter training corpora -->

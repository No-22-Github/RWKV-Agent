# tab-0011 - Thornbury Meadowbank bulk stock value

## Traps
- TR-HEADER: stocktake_2026-09-14.csv opens with two report lines before
  the column names and closes with a "Grand total" line, and the total
  line is wide enough to satisfy the bulk rule (1077 units, well over the
  twenty-unit threshold). A reader who takes the export as a flat tablet
  of rows and adds the value column for everything holding twenty units
  or more sums the eight real bulk lines (9366.95) plus the closing total
  (9435.05) and lands on 18802.00, the registered decoy, which is just
  over twice the real figure.

## Reference solution
1. read_file README.md - line value is units multiplied by the standard
   cost of the SKU, and the standard costs are held in
   standard_costs.csv (1)
2. read_file stocktake_2026-09-14.csv - two report lines, then the column
   names, eleven counted lines and a closing Grand total line (2)
3. read_file standard_costs.csv - the standard cost for each SKU (3)
4. calculator - take the eight lines holding twenty units or more
   (TB-2201, TB-2238, TB-2310, TB-2356, TB-2427, TB-2463, TB-2498,
   TB-2577), multiply units by the standard cost and add: 9366.95 (4)

## Why the answer is unique
The prompt fixes which lines count (twenty units or more) and the README
fixes how a line is valued (units times the standard cost of the SKU).
Only three lines fall under the threshold (TB-2274 with 16,
TB-2392 with 12 and TB-2531 with 18) and TB-2274 sits well clear of the
boundary, so the bulk set is unambiguous. The closing line is the only
row whose first field is not a SKU, and the standard cost file carries
exactly one cost per counted SKU, so the sum has a single value: 9366.95.

<!-- WORKBANK-CANARY-c2a94e71 : this file must never enter training corpora -->

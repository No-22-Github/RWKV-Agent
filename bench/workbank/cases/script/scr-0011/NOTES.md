## Traps
- TR-DEFN: the report is required to state revenue net of the sales tax
  collected on the sales, but the shipped store_revenue.py accumulates
  `gross_amount_cents`, the tax-inclusive figure, while still labelling the
  column `net_revenue_cents`. Doing nothing prints the plausible-but-wrong
  report below; the correct net basis subtracts `tax_cents` per row:

  ```
  store_id,net_revenue_cents
  STR-4407,45615
  STR-5120,76180
  STR-6602,24950
  STR-8813,189700
  total,336445
  ```

  That is the shipped script's output at grading time, where the harness has
  written the second input set (data/sales-2026-09.csv) into the workspace and
  the script's own glob picks it up: STR-6602 is present in the decoy report
  as well as in the correct one, and only the basis separates them. Against
  the visible three extracts alone - what a solver sees while working - the
  same script prints STR-4407 40515, STR-5120 76180, STR-8813 156500,
  total 273195 and no STR-6602 row, so neither the per-store figures nor the
  store list can be hard-coded from the visible data.
  trap_decoys is null (offline-run case; the decoy is that gross-based report).

## Reference solution
1. read_file README.md - the extract's columns and that gross_amount_cents
   already contains the sales tax in tax_cents (1)
2. read_file store_revenue.py - the accumulator reads gross_amount_cents (2)
3. read_file one monthly extract - confirm every row carries both figures, so
   the tax can be taken out per row (3)
4. write_file store_revenue.py - sum gross_amount_cents minus tax_cents per
   store, keeping the header, the ascending store order and the total line (4)

ref_calls = 4.

## Why the answer is unique
The extracts carry whole-cent figures and the tax is always present as its own
field, so "net of the sales tax" resolves to exactly `gross_amount_cents -
tax_cents` with no rounding. A second input set adds a later month and a store
the model never saw, so a hardcoded store list or hardcoded totals fail, and the
byte-exact stdout comparison forces the required:

```
store_id,net_revenue_cents
STR-4407,41509
STR-5120,69324
STR-6602,22704
STR-8813,172627
total,306164
```

<!-- WORKBANK-CANARY-1d94c6be : this file must never enter training corpora -->

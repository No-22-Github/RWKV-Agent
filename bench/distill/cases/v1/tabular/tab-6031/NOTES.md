## Traps
- TR-NUMFMT: both files carry amounts like "$1,240.50", so column aggregation over the raw cells
  errors out and the arithmetic must be done by hand. A reader who subtracts pound figures with
  the pence dropped reports 3632.0 outstanding instead of 3634.55.

## Reference solution
1. List the workspace: the invoice book, the payments book and a readme.
2. Read README.md: payments are receipts against the August invoices.
3. Read both files, total the invoiced amounts and the paid amounts with pence kept, and take the
   difference: 3634.55.

## Why the answer is unique
Outstanding is invoiced less paid, every payment row references an August invoice, and stripping
the currency punctuation leaves one number per row. The pence are part of those numbers, so the
pound-only figure 3632.0 is short by the discarded pence; the true outstanding balance is 3634.55.

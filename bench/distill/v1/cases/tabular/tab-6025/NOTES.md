## Traps
- TR-NUMFMT: amounts are written like "$7,412.20", so column aggregation over the raw cells errors
  out and the sums must be done by hand. A reader who adds the pound figures and drops the pence
  reports 6291.0 for the leading region instead of 6296.21.

## Reference solution
1. List the workspace: the July invoice log and a readme.
2. Read README.md: one row per invoice, amounts in pounds.
3. Read region/invoices_2026-07.csv, total the amounts per region keeping the pence, and take the
   leading region's total: 6296.21.

## Why the answer is unique
Stripping the currency punctuation leaves one number per invoice, and the region column assigns
each invoice to exactly one office, so the leading region's total is fixed. The pound-only figure
6291.0 discards the pence the rows carry; the true total is 6296.21.

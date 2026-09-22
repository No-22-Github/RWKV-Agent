## Traps
- TR-DEFN: the summary must report revenue net of the sales tax billed with the
  goods, but the shipped billing_summary.py accumulates `gross_amount_cents`,
  the tax-inclusive figure, under a `net_revenue_cents` header. Reading every
  row and skipping the tax yields a plausible but wrong report.
- TR-DELIM: the extracts alternate between comma-separated (with customer names
  wrapped because they contain commas) and column-separated layouts, and the
  shipped parser does `line.split(",")` and then discards any row that is not
  exactly six cells. So it silently drops every row of the column-separated
  file (four invoices) and every wrapped row of the comma-separated file
  (INV-7408 and INV-7422) - six of the ten invoices in the visible data,
  leaving only INV-7401, INV-7415, INV-7429 and INV-7436. The shipped script's output is:

  ```
  region,net_revenue_cents
  Coast,80100
  North,100700
  total,180800
  ```

  which is wrong in both bases at once. trap_decoys is null for both (offline-run
  case; the decoy is that truncated, tax-inclusive report).

## Reference solution
1. read_file README.md - the two layouts, the wrapping rule, and the six
   columns including gross_amount_cents / tax_amount_cents (1)
2. read_file billing_summary.py - the single-separator split and the
   `len(cells) != 6` guard that discards the other layout and wrapped rows (2)
3. read_file the comma-separated extract - see the wrapped customer values and
   the column-separated file's field shape (3)
4. write_file billing_summary.py - parse each extract with its own layout
   (quote-aware for the comma-separated one, field-by-field for the other) and
   sum gross_amount_cents minus tax_amount_cents per region (4)

ref_calls = 4.

## Why the answer is unique
The README fixes the two layouts inbound and the six columns, every amount is a
whole number of cents, and the tax is a separate field, so "net of the sales tax"
is exactly `gross_amount_cents - tax_amount_cents` with no rounding. A second
input set adds a further column-separated extract for September, so a script
that hardcodes the visible regions or totals fails; the byte-exact stdout
comparison forces:

```
region,net_revenue_cents
Coast,174174
Midlands,99190
North,155656
total,429020
```

<!-- WORKBANK-CANARY-8f2a6d51 : this file must never enter training corpora -->

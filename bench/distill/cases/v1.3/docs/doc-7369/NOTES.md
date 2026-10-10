## Traps
- TR-NEARNAME: the steward says the orders folder, but orders/ holds received
  invoices and the README sends chandlery purchase lists to purchasing/.
  Writing orders/2026-09-28.txt is the trap.
- TR-DECOY: the day sheet has four rows, but the spinnaker repair tape row is
  quote only (a price check) and stays off the purchase list.

## Reference solution
1. Read README.md: chandlery purchase lists go in purchasing/ named YYYY-MM-DD.txt, one line `- <item> x<qty>` per row whose status is order; orders/ is for received invoices.
2. Read daylogs/2026-09-28.txt.
3. Write purchasing/2026-09-28.txt with the three order rows.

## Why the answer is unique
The README resolves both traps explicitly: the paperwork lives in purchasing/
(the orders folder is the invoice drawer, so a list dropped there would never
reach the chandlery), and quote-only rows are price checks rather than
purchases, so ordering the tape would buy stock nobody asked for. Item names
and quantities come verbatim from the sheet, so the list has exactly one
possible content and one possible location.

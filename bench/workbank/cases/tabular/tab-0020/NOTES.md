## Traps
- TR-TZ: invoices_utc.csv stamps are UTC and metering_sgt.csv stamps are at
  UTC+08:00; the task asks for June 2026 in Singapore time. INV-7765 is stamped
  `2026/06/30 22:15` UTC, which is 1 July 06:15 in Singapore, so it falls
  outside June; INV-7771 is stamped `2026/05/31 21:40` UTC, which is 1 June
  05:40 in Singapore, so it falls inside. Ignoring the stamps' zones and
  filtering on the written date reverses both and gives 46290.55 (registered
  decoy) instead of 54684.80.
- TR-DATEFMT: both files mix `2026/06/04`, `09-06-2026` and `Jun 17, 2026`
  styles, and the README fixes the day-first convention for the bare-number
  ones. Read those month-first and four rows change sides, two each way:
  INV-7748 `09-06-2026` (9 June, inside) leaves as 6 September (-1265.50) and
  MTR-2605 `02/06/2026` (2 June, inside) leaves as 6 February (-735.80),
  while INV-7784 `06/07/2026` (6 July, outside) enters as 7 June (+3375.00)
  and MTR-2671 `06/03/2026` (6 March, outside) enters as 3 June (+1045.00).
  The bare-number rows with no month-first reading - `18-06-2026` and
  `30/06/2026` - fall back to day-first and stay put. 54684.80 - 1265.50 -
  735.80 + 3375.00 + 1045.00 = 57103.50, the registered decoy. The zone shift
  is applied as stated throughout, so this decoy is the date convention alone.

## Reference solution
1. read_file README.md - both files together hold every June charge; the
   invoicing stamps are UTC, the metering stamps are UTC+08:00, and bare-number
   dates are day-first (1)
2. read_file invoices_utc.csv - six invoicing rows (2)
3. read_file metering_sgt.csv - seven metering rows (3)
4. Shift every stamp to Singapore time and keep the rows whose local date is in
   June 2026: from the invoicing ledger keep INV-7731 (4 Jun), INV-7748
   (9 Jun), INV-7752 (18 Jun) and INV-7771 (1 Jun); drop INV-7765 (1 Jul) and
   INV-7784 (6 Jul). From the metering ledger keep every row except MTR-2671,
   which is 6 March (4)
5. Sum 4820.00 + 1265.50 + 18740.25 + 9035.00 = 33860.75 from the invoicing
   ledger and 735.80 + 512.40 + 2240.00 + 11875.60 + 1480.00 + 3980.25 =
   20824.05 from the metering ledger: 33860.75 + 20824.05 = 54684.80 (5)

The answer is 54684.80.

## Why the answer is unique
The README states that the two files partition the month's charges, so the
answer necessarily takes both: the invoicing ledger alone gives 33860.75 and
the metering ledger alone gives 20824.05, neither of which is the month's
total. Each stamp is read under a single rule (day-first for bare-number dates,
month named or year-first otherwise) and then shifted by the zone the README
assigns to its file, which places every row inside or outside June exactly
once. The two registered decoys come from defensible-looking but contradicted
readings: 57103.50 from swapping the day and month on the bare-number dates,
and 46290.55 from ignoring the zone labels the README states.

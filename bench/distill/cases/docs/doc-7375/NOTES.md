## Traps
- TR-DECOY: the sheet lists three patients, but Juniper's doxycycline is
  routed to the outside pharmacy and never enters the dispensary ledger.
  Ledgering all three is the trap.

## Reference solution
1. Read README.md: dispensary rows become `<date> <patient> - <item> - dispensed - <vet>` lines appended to the monthly ledger; outside pharmacy rows never enter it.
2. Read notes/scripts-2026-09-28.txt.
3. Read the existing ledger lines to match the style.
4. Append the Pepper and Waffle lines dated 2026-09-28.

## Why the answer is unique
The sheet routes Juniper's item to the outside pharmacy, which the README
excludes from the ledger, so ledgering it would record a dispense that never
happened in-house. The two dispensary rows carry their date, patients, items
and vet from the sheet, and the line shape is fixed by the existing ledger, so
the appended block is exactly two lines.

## Traps
- None declared. The scoring run adds a second monthly export the model never
  saw (expect.run.hidden_files, kept inside ledgers/), so a script that reads
  only the file it opened during exploration, or that hardcodes September's
  rows, prints four day lines and fails the run check.

## Reference solution
1. Read bookings.py: its notes fix the layout (one line per day, then TOTAL).
2. Read ledgers/2026-09.csv to confirm the export columns.
3. Write bookings.py: sweep every ledgers/*.csv, skip each header, aggregate
   per booked_on the booking count and the pence total, print in date order,
   then the TOTAL line.

## Why the answer is unique
The merged exports fix every number: 2026-09-03 carries two bookings for 6600
pence, 2026-09-09 one for 5100, 2026-09-14 one for 4400, 2026-09-21 one for
1700, 2026-10-02 one for 3400 and 2026-10-11 two for 10500, so the printout is
exactly seven lines ending TOTAL,8,31700. The layout is pinned by the notes
inside bookings.py, and the scoring run supplies ledgers/2026-10.csv, so a
September-hardcoded script and a single-file script both miss the October day
lines and differ from the expected stdout.

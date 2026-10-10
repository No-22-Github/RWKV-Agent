## Traps
- TR-DUPROW: dispatch_log_2026-07.csv reprints five consignments, all of them under their original dispatch_id,
  so counting the 63 data lines gives 63 notes rather than 58.

## Reference solution
1. List the workspace: the July dispatch log and a short readme.
2. Read README.md: one note per consignment, and the export was started again, so notes can appear twice.
3. Read dispatch_log_2026-07.csv and count one note per distinct dispatch_id: 58 notes.

## Why the answer is unique
The readme states one note per consignment, and each reprinted line repeats its dispatch_id, date, market,
variety and bunch count exactly, so the repeats are the same consignment written out again rather than a second
one. Counting distinct dispatch_id values leaves 58 notes for the month.

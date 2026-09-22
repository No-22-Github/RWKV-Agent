## Traps
- TR-DUPROW: campaign exports repeat whole event lines, and the archive
  counts each subscription event once. `EV-7321` repeats inside
  `archive/2026-05/events-a.csv`, `EV-7314` appears in `-a` and again in
  `archive/2026-05/events-b.csv`, and `EV-7402` appears in
  `archive/2026-q3/events-c.csv` and again in
  `archive/2026-06/late/events-d.csv`; the hidden
  `archive/2026-08/events-e.csv` repeats `EV-7463`. Counting rows
  instead of events gives the decoy

      2026-04,2598
      2026-05,32697
      2026-06,30099
      2026-07,18297
      2026-08,1299
      2026-09,15699
      total,100689

  (`trap_decoys.TR-DUPROW` is null; script case, concrete wrong stdout
  recorded here).
- TR-DATEFMT: `occurred` is written three ways - ISO `2026/05/19`,
  day-first `22-05-2026`, and the English form `Jun 3 2026`. The README
  fixes the day-first convention. The load-bearing record is `EV-7402`
  at `03-04-2026`, which is 3 April 2026 under the stated convention but
  4 March 2026 if read month-first, so a month-first solver invents a
  `2026-03` line and empties `2026-04`. A second, weaker decoy is
  grouping by the campaign folder: the folders are named `2026-05`,
  `2026-q3`, `2026-06`, `2026-08` while the rows inside them belong to
  April, June, July and August, so a folder-based roll-up produces a
  different month set entirely. `trap_decoys.TR-DATEFMT` is null; the
  concrete wrong bucket is the `2026-03` / empty `2026-04` split above.

## Reference solution
1. list_files - README, the stub, the archive/ campaign folders, the
   unrelated send schedule (1)
2. read_file README.md - columns, per-event rule, month grouping, the
   three date shapes and the day-first convention (2)
3. read_file archive/2026-05/events-a.csv - see the mixed dates and a
   repeated event line (3)
4. read_file archive/2026-q3/events-c.csv - see a row whose real month
   differs from its folder and the ambiguous `03-04-2026` record (4)
5. write_file archive_rollup.py - walk the tree for every events-*.csv,
   count each event_id once, parse occurred in all three shapes,
   group by YYYY-MM and print the lines plus the total (5)

ref_calls = 5.

## Why the answer is unique
The README fixes the event identity, the day-first convention, the month
grouping (by occurred, not by folder), the ascending order and the total
line; amounts are integer cents, so the scored stdout has one value:

    month,amount_cents
    2026-04,1299
    2026-05,16998
    2026-06,30099
    2026-07,16998
    2026-08,1299
    2026-09,15699
    total,82392

The hidden sheet adds August and September and repeats a July event, so a
hard-coded report fails and the de-duplication has to span the whole
tree. `files` is read by verify.py, so corrupting a visible export moves
the expected stdout.

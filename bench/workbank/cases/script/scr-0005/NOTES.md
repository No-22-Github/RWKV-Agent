# WORKBANK-CANARY-5a1d7c93 : bank artifact, excluded from training corpora

## Traps
- None. This is the family's plain base task: the layout (one
  `<rig_id> <minutes>` line per instrument in ascending rig_id order,
  then `grand <total>`), the grouping column and the aggregate are all
  stated in the prompt, and every `minutes` value in every export is a
  bare integer, so there is no reading to get wrong. The only thing
  tested is whether the sweep actually reaches the second input set the
  harness writes in before running (bookings/2026-09/rig-bookings.csv,
  nested two directories down), which is what defeats a hard-coded
  answer. trap_decoys is empty (no traps).

## Reference solution
1. list_files - bookings/, README.md, the maintenance log: the export
   tree and its nesting (1)
2. read_file README.md - launch contract: run from the project root,
   export named rig-bookings.csv at unfixed depth, column semantics (2)
3. write_file tally.py - recursive sweep for rig-bookings.csv, sum the
   minutes column per rig_id, print ascending rig lines plus the grand
   line (3)

ref_calls = 3.

## Why the answer is unique
The prompt pins the layout, the grouping key, the order and the closing
line; the README pins the export name and the `minutes` column meaning;
the files sum to whole minutes, so no rounding is open. The hidden
September export adds minutes to every rig already present and is
reached by the same recursive sweep, so the printed summary is the one
byte-exact stdout and a memorised or hard-coded total fails.

<!-- WORKBANK-CANARY-5a1d7c93 : this file must never enter training corpora -->

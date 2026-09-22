# WORKBANK-CANARY-0d93f5ae : bank artifact, excluded from training corpora

## Traps
- TR-RULEFILE: the figure, its one-decimal half-up rounding and the
  handling of runs with no reading all live in monitoring_protocol.md,
  not in the prompt. The rounding clause bites on Northgate, whose four
  recorded readings (42,47,39,53) sum to 181: 181/4 = 45.25 -> 45.3
  with halves up, but 45.2 if the script rounds to even. Not reading the
  protocol leaves the figure and its rounding undefined.
- TR-MISSING: the micro_index column mixes three forms of run that
  produced no reading - the letters NA, a dash, and an empty field -
  and they appear in both input sets (visible: S-3304 NA, S-3308 -,
  S-3310 empty; hidden: S-3402 -, S-3405 NA, S-3408 empty, S-3423 NA,
  S-3432 empty). A script that treats them as zero, or divides by the
  row count instead of the recorded count, is wrong: Northgate has 4
  readings, not its 7 rows.
  The decoys are the means taken over all rows (Northgate 181/7 ->
  25.9), a naive int() on the column (crash on the dash), and a
  count that includes the no-reading runs. The harness writes in a
  second input set the model never saw (sites/2026-w35/...), whose
  proportion of no-reading runs is roughly double the visible set's
  (5 of 11 vs 3 of 12), so a hard-coded summary fails.
  trap_decoys is null (write/script case).

## Reference solution
1. list_files - README.md, monitoring_protocol.md, sites/ holding the
   analyser export, the calibration log: project shape (1)
2. read_file README.md - launch contract: run from the project root,
   exports named air-samples-*.csv at unfixed depth (2)
3. read_file monitoring_protocol.md - mean of recorded readings to one
   decimal with halves up, no-reading runs excluded from mean and count,
   the station,readings,mean layout (3)
4. read_file sites/air-samples-2026-w32.csv - the three no-reading forms
   and the column names (4)
5. write_file station_summary.py - recursive sweep for air-samples-*.csv,
   skip the three no-reading forms, per-station sum and recorded count,
   half-up mean to one decimal, print the header and ascending rows (5)

ref_calls = 5.

## Why the answer is unique
The protocol fixes the statistic (mean of recorded readings), the
rounding (one decimal, halves up) and the counting rule (no-reading
runs excluded from both mean and count); the layout is fixed to the
header plus ascending station rows. The only half case in the combined
data is Northgate's 45.25 -> 45.3, and each station's recorded count is
unambiguous. The hidden second export changes the counts, the set of
stations (it adds Dunmere) and each mean, so the single correct stdout
cannot be produced from the visible export alone.

Both analyser exports sit under sites/ - the visible one straight in it,
the hidden one inside a dated week folder below it - which is the pair of
shapes README.md declares. A sweep rooted at sites/ and a sweep of the
whole project tree therefore see the same files and print the same
summary; v1 left the visible export at the project root, where a script
written to the README's own wording missed it and dropped Northgate.

<!-- WORKBANK-CANARY-0d93f5ae : this file must never enter training corpora -->

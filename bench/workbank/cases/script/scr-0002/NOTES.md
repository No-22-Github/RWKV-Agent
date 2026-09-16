## Traps
- TR-RULEFILE: the manifest layout AND the line ordering live in
  outbound_spec.md, including the clause that priority=yes shipments jump
  ahead of everything else (ordered by order_id among themselves). Not
  reading the spec file guarantees a wrong stdout. Two concrete near-misses:
  (a) only repairing the KeyError ('carrier' -> 'carrier_service') yields a
  script that runs and prints a plausible five-column manifest in input-file
  order; (b) sorting plainly by (carrier_service, order_id) buries the two
  priority rows W61-1017 / W61-1051 inside their carrier groups. Both fail
  the byte-exact stdout comparison. trap_decoys is null (write/script case).

## Reference solution
1. read_file README.md - on-call note with the real traceback
   (KeyError: 'carrier') (1)
2. read_file pick_pack.py - stale column name, unsorted five-column print
   loop (2)
3. read_file outbound_spec.md - print columns (zone dropped), header, and
   the priority-first ordering clause (3)
4. write_file pick_pack.py - read carrier_service, priority rows first
   (by order_id), the rest grouped by carrier_service then order_id,
   four-column output with header (4)

ref_calls = 4. (Peeking at wave_61.csv is prudent but not required: the spec
names the columns and the fix is data-independent.)

## Why the answer is unique
The traceback pins the crash, the spec pins the column set, header and
ordering; the priority clause changes the row order for this exact wave and
the zone drop changes every line, so any of the plausible near-misses
diverges in the line-by-line stdout comparison.

<!-- WORKBANK-CANARY-9d07c3f5 : this file must never enter training corpora -->

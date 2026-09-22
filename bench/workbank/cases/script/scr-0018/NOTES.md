## Traps
- TR-DUPROW: whole duplicated load lines are exported by the depot
  tooling, and the roll-up has to total crates per produce line over the
  loads rather than over rows. The repeats are spread through the
  sheets: `LD-4112` twice inside `depots/coastal/shipments-a.csv`,
  `LD-4107` once in `-a` and again in `depots/coastal/shipments-b.csv`,
  `LD-4208` twice inside `depots/inland/shipments-c.csv`, and in the
  hidden `depots/coastal/shipments-e.csv` the loads `LD-4124` and
  `LD-4112` repeat earlier sheets while `LD-4350` repeats inside the same
  sheet. Counting every row instead of every load gives

      Chicory,116
      Kale,203
      Rhubarb,131
      Spinach,209
      total,659

  which is the decoy (`trap_decoys.TR-DUPROW` is null because this is a
  script case with no single scalar answer, so the concrete wrong stdout
  is recorded here). The hidden sheet carries a *different* spread of
  repeats - one wholly inside itself and two carried over from the
  visible tree - so a solver that de-duplicates per file rather than
  across the whole tree is wrong in a third way again, printing

      Chicory,64
      Kale,203
      Rhubarb,114
      Spinach,209
      total,590

  which is neither the correct roll-up (468) nor the row-count decoy (659).
  Per-file de-duplication catches only the repeats that sit inside one sheet
  (LD-4112 in -a, LD-4208 in -c, LD-4350 in the hidden -e) and misses every
  load carried across sheets.

## Reference solution
1. list_files - README, the stub, the depots tree, the unrelated SOP (1)
2. read_file README.md - sheet columns, the per-load rule, printed
   layout and ascending produce order (2)
3. read_file depots/coastal/shipments-a.csv - see the sheet shape and
   the repeated load lines (3)
4. write_file depot_rollup.py - walk the tree for every shipments-*.csv,
   count each load_id once globally, sum crates per produce, print the
   lines plus the total (4)

ref_calls = 4.

## Why the answer is unique
The README fixes the identity rule (a load_id is one physical load and
totals are taken over loads), the layout, the ascending produce order and
the total line, all amounts are integer crates, so the scored stdout has
exactly one value:

    produce,crates
    Chicory,64
    Kale,161
    Rhubarb,97
    Spinach,146
    total,468

The hidden second sheet defeats hard-coding and forces the de-duplication
to be global: `LD-4124` and `LD-4112` reappear there yet must not be
counted again, and a fresh load `LD-4355` enters Kale. `files` is read by
verify.py, so corrupting a visible sheet moves the expected stdout.

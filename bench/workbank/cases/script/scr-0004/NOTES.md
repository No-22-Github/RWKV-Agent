## Traps
- TR-RULEFILE: the counting definition lives in settlement_spec.md and this
  dataset hits every clause: settled-only (a pending and a failed row would
  swing totals by 12500 / 41000 / 2400000), type=refund subtracts (MER-3014,
  MER-3068, MER-3052, MER-3091), and channel=internal rows are dropped even
  when settled (MER-3052 158000 in July, MER-3014 450000 and MER-3027 73400
  in the hidden September file). Not reading the spec guarantees a wrong
  stdout. On top, the run uses a second input set the model never saw
  (hidden/transactions-2026-09-eu.csv): it adds merchant MER-3106 and flips
  MER-3052's total, so hard-coded totals and sweeps anchored to the visible
  files both fail. trap_decoys is null (write/script case).

## Reference solution
1. list_files - extracts, spec, README, the report.py shell (1)
2. read_file README.md - launch contract: run from the project root, sweep
   the whole tree for transactions-*.csv (2)
3. read_file settlement_spec.md - settled-only, internal excluded, refunds
   subtract, layout and ascending merchant order (3)
4. read_file transactions-2026-07-eu.csv - confirm columns and row shapes (4)
5. read_file transactions-2026-08-eu.csv (5)
6. write_file report.py - recursive sweep from the launch directory, spec
   filter, integer-cent totals, sorted merchant lines plus grand total (6)

ref_calls = 6.

## Why the answer is unique
The spec pins which rows count, the direction of refunds, the layout and the
ascending merchant order; all amounts are integer cents so no rounding is
left open; every merchant's net is positive and no merchant exists only
through internal rows, so there is no omit-vs-print-zero ambiguity. The
byte-exact stdout comparison closes the case, and the hidden September
extract makes one-true-output robust against hardcoding.

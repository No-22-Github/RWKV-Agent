## Traps
- TR-RULEFILE: the counting definition lives in settlement_spec.md and this
  dataset hits every clause: settled-only (a pending and a failed row would
  swing totals by 12500 / 41000 / 2400000), type=refund subtracts (MER-3014,
  MER-3068, MER-3052, MER-3091), and channel=internal rows are dropped even
  when settled (MER-3052 158000 in July, MER-3014 450000 and MER-3027 73400
  in the hidden September file). Not reading the spec guarantees a wrong
  stdout. On top, the run uses a second input set the model never saw
  (batches/2026-09/transactions-2026-09-eu.csv, written into the workspace
  copy before the script runs): it adds merchant MER-3106 and flips
  MER-3052's total, so hard-coded totals fail, and it sits two directories
  down so a sweep that only looks at the top level misses it. What the case
  does *not* test is which anchor the sweep is rooted at: the hidden set is
  inside the project tree, so os.getcwd() and the script's own directory both
  reach it. trap_decoys is null (write/script case).

## Reference solution
1. list_files - extracts, spec, README, the report.py shell (1)
2. read_file README.md - launch contract: run from the project root, sweep
   the whole tree for transactions-*.csv (2)
3. read_file settlement_spec.md - settled-only, internal excluded, refunds
   subtract, layout and ascending merchant order (3)
4. read_file transactions-2026-07-eu.csv - confirm columns and row shapes (4)
5. read_file transactions-2026-08-eu.csv (5)
6. write_file report.py - recursive sweep of the project tree, spec
   filter, integer-cent totals, sorted merchant lines plus grand total (6)

ref_calls = 6.

## Why the answer is unique
The spec pins which rows count, the direction of refunds, the layout and the
ascending merchant order; all amounts are integer cents so no rounding is
left open; every merchant's net is positive and no merchant exists only
through internal rows, so there is no omit-vs-print-zero ambiguity. The
byte-exact stdout comparison closes the case, and the hidden September
extract makes one-true-output robust against hardcoding.

## Reviewer notes
- v2 (2026-09-21 audit): the hidden extract moved from `hidden/` to
  `batches/2026-09/` inside the workspace. It used to be written beside the
  workspace copy while the script ran from the sandbox root, so a sweep rooted
  at `os.getcwd()` saw it and a sweep rooted at `Path(__file__).parent` did
  not - and scr-0001..0003 all anchor on `__file__`, so the bank's own
  fixtures taught the idiom this case silently failed. The harness now writes
  hidden files inside the workspace copy and runs the script with that
  directory as its working directory, which is what the README already
  described. Expected stdout is unchanged: same rows, same totals.

<!-- WORKBANK-CANARY-3f9b70c8 : this file must never enter training corpora -->

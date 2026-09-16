## Traps
None - L0 baseline of fam-script-etl-01. The shipped convert.py is a
placeholder that exits non-zero, so replying DONE without rebuilding it fails
the offline run.

## Reference solution
1. read_file data.json - shape of the invoices array (1)
2. read_file README.md - column semantics; totals are integer cents, account
   names never contain commas (2)
3. write_file convert.py - input resolved next to the script (scheduler runs
   it from its own working directory), fixed header, one line per record in
   JSON array order (3)

ref_calls = 3.

## Why the answer is unique
The prompt pins the header, the column order and the row order (same as the
JSON array); the data has no commas or quotes, so no CSV quoting decision is
left open, and the offline comparison is byte-exact per line.

<!-- WORKBANK-CANARY-b4f2e91a : this file must never enter training corpora -->

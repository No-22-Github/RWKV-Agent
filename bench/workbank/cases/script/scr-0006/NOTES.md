# WORKBANK-CANARY-e2b84f10 : bank artifact, excluded from training corpora

## Traps
- TR-RULEFILE: pooling, the demurrage clause and the rounding all live
  in depot_report_spec.md, not in the prompt. Three clauses bite on this
  data. (a) kind=demurrage entries never go to the account that
  triggered them but pool into one DEMURRAGE line, and the pooled total
  is not a rounding-free number: 7600+3300 (visible) + 5250+8800+6300
  (hidden) = 31250 cents -> 312.50 euros -> 313. Charging demurrage back
  to its account instead yields account lines for Ardent Freight /
  Belport Cargo / Cintra Haulage / Dunmore Lines and no DEMURRAGE line,
  a wholly different stdout. (b) figures are stated in whole euros with
  halves rounded up: Ardent Freight's handling sums to 73250 cents =
  732.50 -> 733 (a script using banker's rounding prints 732), and
  Dunmore Lines sums to 40050 cents = 400.50 -> 401 (banker's gives
  400). (c) the report is alphabetical by account, then DEMURRAGE last.
  Reading none of the spec yields cents figures in file order. On top,
  the harness writes in a second extract the model never saw
  (depot/2026-09/charges-2026-09.csv, two directories down) which adds
  Dunmore Lines and changes the pooled figure, so a hard-coded answer
  fails. trap_decoys is null (write/script case).

## Reference solution
1. list_files - README.md, depot_report_spec.md, the depot extract, the
   contact list: project shape (1)
2. read_file README.md - launch contract: run from the project root,
   extracts named charges-*.csv at unfixed depth (2)
3. read_file depot_report_spec.md - pool by account, demurrage pooled
   depot-wide, whole euros with halves rounded up, account order plus
   the DEMURRAGE last line (3)
4. write_file chargeback_report.py - recursive sweep of the project
   tree, split demurrage from account charges, cents-to-euros with
   half-up rounding, print the pooled layout (4)

ref_calls = 4. (Peeking at depot/charges-2026-07.csv is prudent but not
required: the spec names the columns.)

## Why the answer is unique
The spec pins the grouping key (account), the demurrage carve-out, the
half-up euro rounding and the line order; every amount is integer cents,
so the only open step is the rounding the spec fixes. Every account's
euro figure is unambiguous and the pooled DEMURRAGE line is the sum of
exactly five demurrage entries. The hidden September extract and the
byte-exact stdout comparison make the single correct rendering robust
against hardcoding.

<!-- WORKBANK-CANARY-e2b84f10 : this file must never enter training corpora -->

## Traps
- TR-NUMFMT: the `amount` column of the ledger exports arrives exactly as the
  ledger emits it - `$1,204.50`, `$86.40`, and credits in parentheses such as
  `(318.75)`. Nothing in the workspace converts it: the shipped takings.py is
  the pre-migration version that handed bare decimals to pandas, the replay
  host has no pandas at all, and the exports the ledger now writes are the
  only ones in the tree. The rewrite has to parse the column itself. Two
  concrete misreadings: (a) `float(row["amount"])` or
  `int(row["amount"].replace(",", ""))` raises ValueError on every row and the
  job prints nothing at all; (b) stripping everything except digits and the
  decimal point turns the credits positive, which lifts AR-2201 from 337900 to
  401650, AR-2247 from 342575 to 530575, AR-2258 from 1215 to 42295 and the
  grand total from 914685 to 1207515. trap_decoys is null (the case is scored
  on the script's stdout, which has no single decoy line).

## Reference solution
1. read_file README.md - the printed layout, the cents unit, and the
   convention that credits sit in parentheses and reduce their account (1)
2. read_file takings.py - the glob over exports/*.csv and the print code, and
   why the job cannot run: it feeds the amount column straight to a package
   the replay host does not have (2)
3. read_file exports/2026-07.csv - the amount column as it now arrives from the
   ledger (3)
4. write_file takings.py - stdlib csv reader behind the same glob, amounts
   parsed from the ledger spelling (sign from the parentheses, exact cents),
   same header, account order and total line (4)

ref_calls = 4.

## Why the answer is unique
README.md pins the layout, the whole-cents unit and the credit convention, so
the reading of `(318.75)` is stated rather than guessed: treating it as
positive contradicts the documented convention and produces 1207515, and
`float()` on the raw column produces no output at all. The exports are plain
three-column CSV, so the only remaining decision is the arithmetic, which is
exact in cents. The hidden month is the same shape and just extends each
account's running net, so hardcoded figures fail. The one stdout the post-run
workspace can produce is

  account,net_cents
  AR-2201,337900
  AR-2233,232995
  AR-2247,342575
  AR-2258,1215
  total,914685

<!-- WORKBANK-CANARY-4c9f2e80 : this file must never enter training corpora -->

## Traps
- TR-NEARNAME: the correction names storefront-september.csv, but the ledger on disk is
  storefront-2026-09.csv (the README states the naming scheme). A model that fails to match
  the name falls back on the most conspicuous figure nearby - the 210-copy day.

## Reference solution
1. read_file transfers-2026-09.csv. Turn 1: transfer copies sum to 856 册.
2. list_files: the ledgers on disk are transfers-2026-09.csv and storefront-2026-09.csv.
3. read_file storefront-2026-09.csv. Turn 2: retail copies sum to 1290 册. Turn 3: the biggest single day is 青箱记 with 210.

## Why the answer is unique
No file is named storefront-september.csv, and the README's naming scheme plus the single storefront ledger leave exactly one retail record; its copies sum to 1290, distinct from the transfers total 856. The largest single-day figure on that ledger is 青箱记's 210, which is a per-day count, not the monthly total.

## Five alternative phrasings of the task
1. xingqiao bookstore september ledgers
2. warehouse transfer copies in september
3. storefront retail copies in september
4. the retail ledger under its real name
5. best single sales day in the storefront ledger

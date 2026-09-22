## Traps
- None. The task is a plain ranking of one table. There are no repeated rows,
  no total line, and no misformatted numbers; the ledger carries one row per
  account with a unique annualized value.

## Reference solution
1. read_file README.md - the ledger holds one row per account and
   annual_value_usd is the full-year committed value in USD (1)
2. read_file contract_ledger.csv - ten accounts, each with a distinct
   annualized value (2)
3. Order the ten values descending: 148900.00 (MRA-2088), 132600.00
   (MRA-2189), 62340.00 (MRA-2160), 48950.00 (MRA-2041), 41780.75
   (MRA-2231), 18975.25 (MRA-2137), 12750.50 (MRA-2063), 9640.00 (MRA-2258),
   3480.00 (MRA-2114), 2260.00 (MRA-2205). The third-largest is MRA-2160 (3).

The answer is the account code MRA-2160.

## Why the answer is unique
Every row of contract_ledger.csv has a different annual_value_usd, so the
descending order is total and the third position is determined. The ledger is
the only source of account values in the workspace; ops/renewal-notes.txt
carries no amounts and names no accounts that are absent from the ledger.
Reading the file as-is gives MRA-2160 whichever way the rows are ordered,
because a rank is invariant under the order the rows happen to appear in.

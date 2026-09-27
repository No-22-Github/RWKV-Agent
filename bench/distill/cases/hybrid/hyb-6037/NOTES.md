## Traps
- TR-NUMFMT: amounts print with a currency symbol and group separators, so the column cannot be aggregated as numbers. Tallying by eye and dropping the cents gives 3756.0 for August instead of 3757.75.

## Reference solution
1. Turn 1: list_files to find the job billing export.
2. read billing/aug-sep-2026.csv; the amount column errors out in aggregation tools, so the amounts are read cell by cell.
3. add the Brackley Couriers August amounts with the calculator: 1284.60 + 942.30 + 1530.85 = 3757.75.
4. Turn 2 needs no further call: the same read holds the September Brackley amounts, 1105.40 + 876.25 = 1981.65.

## Why the answer is unique
The wording fixes Brackley Couriers as the account, and the follow-up only moves the month to September, whose lines are in the same read. Dropping cents fails on both months because the printed amounts carry exact small change; the 3757.75 August reading loses the cents on three lines. Other fleets belong to other accounts.

## Five alternative phrasings of the task
1. copperside motors brackley couriers august charges
2. brackley couriers september workshop bill
3. copperside fleet job billing august
4. what did brackley couriers run up in august
5. copperside motors job amounts aug-sep

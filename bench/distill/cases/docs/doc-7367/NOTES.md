## Traps
- TR-DECOY: the purchase note lists three items but the 鱼饵 row is 挂账
  (on account, collected later by the accountant). Booking all three is the
  trap; only the two 已结清 rows enter the ledger.

## Reference solution
1. Read README.md: the ledger takes one line per settled purchase with the fields 日期 品名 数量 途径 结算 经手; 挂账 rows wait for the accountant.
2. Read notes/purchase-2026-09-28.txt.
3. Read the tail of logbook/supply-2026-09.txt to match the line style.
4. Append the 机油 and 缆绳 lines dated 2026-09-28.

## Why the answer is unique
The note itself marks 鱼饵 as 挂账 and the house rule defers those rows to the
accountant, so appending it would book a debt that is not settled. The two
settled rows carry their date, quantities and handler from the note, and the
line shape is fixed by the existing ledger rows, so the appended block is
exactly two lines.

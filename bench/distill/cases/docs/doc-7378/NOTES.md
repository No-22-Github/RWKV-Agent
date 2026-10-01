## Traps
- TR-NEARNAME: orders/ holds the current 2026-09.txt and the similarly named
  prior/2026-08.txt; the August ledger is carried-forward record only, so
  pulling rows from it is the trap. The sheet also invites the bare-date name
  pickup/2026-09-28.txt, while the README's pattern is 提货单-YYYY-MM-DD.txt.
- TR-DECOY: the September ledger shows the 500ml装 batch as 已提; listing it
  as still to pick up is the second trap.

## Reference solution
1. Read README.md: the pickup list takes 未提 rows of the current month's ledger, one line `- <品名> <规格> <数量> <客户>` in ledger order, into pickup/提货单-YYYY-MM-DD.txt dated today.
2. Read both order ledgers and tell the current month from the carried-forward one.
3. Read the rows of orders/2026-09.txt and keep the two 未提 rows.
4. Write pickup/提货单-2026-09-28.txt with the two lines.

## Why the answer is unique
提货单的来源被 README 固定为当月登记，prior/ 是结转留底；状态为已提的
500ml装 批次已经有提货记录，再列一遍等于重复发货。两个未提品项的字段全部
照抄登记，行序与文件名由 README 固定，提货单只有一种。

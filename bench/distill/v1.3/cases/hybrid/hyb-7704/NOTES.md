## Traps
- TR-DUPROW: orders/backlog-2026-09.csv repeats DY-2002 (杭州, 零售, 34 件) as two identical
  rows. Summing Hangzhou rows gives 380; summing distinct Hangzhou orders gives 346.

## Reference solution
1. read_file README.md: the export retried, so an order can appear as two identical rows.
2. read_file orders/backlog-2026-09.csv. Turn 1: distinct Hangzhou orders sum to 346 件. Turn 2: the 批发 subset sums to 252 件. Turn 3: 批发+杭州 orders by customer are 纸飞机文具 3 (DY-2001/2012/2017), 蓝格子文创 2.
3. Turn 4: 纸飞机文具's Hangzhou wholesale quantity is 88 + 44 + 58 = 190 件.

## Why the answer is unique
Counting rows gives 380, but DY-2002 appears twice in every column and the README says repeats are the same order, so the second row is not a separate order. Within the wholesale cut only two customers appear, with clearly different order counts and quantities, so 346, 248, 纸飞机文具 and 190 are the only readings.

## Five alternative phrasings of the task
1. lanxi stationery september hangzhou backlog quantity
2. how many pieces ship to hangzhou in the september backlog
3. wholesale-channel hangzhou pieces in september
4. which wholesale customer placed the most hangzhou orders
5. september backlog by channel city and customer

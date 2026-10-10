## Traps
- TR-DECOY: the register has four rows but 402房 地巾 is marked 不算损耗
  (held back from the wash, nothing damaged). Copying all four rows into the
  restock list is the trap.

## Reference solution
1. Read README.md: rows whose 处理 field reads 报废 go on the restock list, one line `- <房号> <品名> <数量>` in register order, file named after the register date.
2. Read records/loss-2026-09-27.txt.
3. Write restock/2026-09-27.txt with the 209房, 305房 and 208房 lines.

## Why the answer is unique
补货只看处理=报废的行；402房 一行的处理是不算损耗，登记里没有给它任何
补货依据，把它写进补货单等于凭空报损。其余三行均为报废，行序与写法由
README 固定，补货单只有一种。

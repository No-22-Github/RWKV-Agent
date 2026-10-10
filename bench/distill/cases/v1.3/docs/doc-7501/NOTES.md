## Traps
- TR-DECOY: reports/duty-handover-0930.txt 的 09-29 盘点行带着备件 BT-2214，看起来像待办，但同一行写明已入库、无遗留。 A careless pass reports `BT-2214`.

## Reference solution
1. List reports/ to find the handover log.
2. Read README.md for the closed/open line convention.
3. Read reports/duty-handover-0930.txt and collect the lines still carrying 待/未/挂起, then answer.

## Why the answer is unique
BT-2214 sits on a line that ends with 已入库、无遗留, and the README defines closed lines by their status words, so it is not an open item. The only lines still carrying 待/挂起/未 are the J-308 ticket line and the BX-2107 line, and no other reading turns a closed line into an open one.

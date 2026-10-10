## Traps
- TR-AMBIG: "current statement period" names no dates and the log covers July through early September; totalling every Oatfield Dairy line gives 277.02, which mixes three periods.

## Reference solution
1. Turn 1: the statement period is a required parameter only the user knows; ask which period the statement covers (no tool calls).
2. Turn 2: the user gives August 2026.
3. Read logs/deliveries.csv, keep Oatfield Dairy rows dated 2026-08: 40.48, 41.40, 39.90, 38.64.
4. Total 160.42 and reply with the number alone.

## Why the answer is unique
 The decoy 277.02 adds the July and September lines; with the period pinned to August 2026 those rows fall outside the statement, so the total is 160.42 under any careful reading. Turn 1 only has to surface the missing period.

## Five alternative phrasings of the task
1. What do we owe Oatfield Dairy this period?
2. Total the Oatfield Dairy invoices for the statement.
3. Add up what Oatfield Dairy charged us.
4. I need the Oatfield Dairy spend for the current statement.
5. How much did Oatfield Dairy bill us this statement?

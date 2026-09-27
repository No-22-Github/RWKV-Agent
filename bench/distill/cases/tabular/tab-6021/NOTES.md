## Traps
- TR-DEFN: the ranking is over clients' combined spend, but the most eye-catching numbers are the
  single order amounts. A reader who ranks individual orders and takes the second-largest reports
  5150.0 instead of the second-ranked client's combined 10378.78.

## Reference solution
1. List the workspace: the August order log and a readme.
2. Read README.md: several clients order more than once a month.
3. Read trade_sales/orders_2026-08.csv, total the amount per client, and take the second-highest
   total: 10378.78.

## Why the answer is unique
The prompt ranks clients by combined spend, and the readme confirms clients place several orders,
so a single order amount is never a client's standing. Summing per client gives one total each
with a clear second place; the decoy 5150.0 is one line inside another client's month. The answer is
10378.78.

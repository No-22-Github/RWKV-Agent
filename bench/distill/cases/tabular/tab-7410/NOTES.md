## Traps
- TR-DUPROW: in orders/sept_orders.csv four September wholesale orders (BC-2609001, BC-2609007, BC-2609013, BC-2609017) were written twice by the retried export, and 5 of the 17 accounts placed a second order. Counting rows gives 26; counting distinct orders gives 22; the task asks for different customers, so the answer is 17 accounts.

## Reference solution
1. Read README.md: customer_id identifies the account, one account can hold several orders, and the retried export rewrote some orders.
2. Aggregate: {{"path":"orders/sept_orders.csv","filter":{{"sales_channel":"Wholesale","order_month":"2026-09"}},"operation":"distinct_count","field":"customer_id"}} gives 17.
3. Reply with the number 17 only.

## Why the answer is unique
The decoy 26 counts rows, re-counting repeated orders and multi-order accounts; 22 counts distinct orders, but the task asks for different accounts. The README states customer_id identifies the account and repeats match their originals, so the distinct-customer reading is the only one. The answer is 17.

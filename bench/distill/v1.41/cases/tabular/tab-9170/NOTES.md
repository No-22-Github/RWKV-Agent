## Traps
- TR-DECOY: 'delivered-late' starts with 'delivered'; a prefix or substring match puts Harbor Foods on top instead.
- TR-MULTISRC: three monthly files must be pooled.

## Reference solution
1. bash: `cat orders/*.csv | awk -F, '$3=="delivered" {c[$2]++} END{for (k in c) print c[k], k}' | sort -rn | head -1`
Final answer: Teramo SpA has the most delivered orders (27).

## Why the answer is unique
Status is an exact column value; the leader is ahead of the runner-up by at least four orders.

## Five alternative phrasings of the task
1. Which customer has the most delivered orders in the Q3 files? The counting rule is in orders/README.md.
2. Across the three monthly order files, who has the highest number of orders with status 'delivered'?
3. Find the top customer by delivered orders (status exactly 'delivered') in orders/.
4. Looking at July to September orders, which customer leads on delivered orders? Check orders/README.md for what counts.
5. Name the customer with the largest count of delivered orders in the order files.

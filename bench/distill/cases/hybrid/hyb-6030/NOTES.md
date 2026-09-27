## Traps
- TR-DUPROW: orders CS-8821 and CS-8824 (both Brindle & Co) appear twice because the export retried. Counting Brindle rows instead of orders gives 8.

## Reference solution
1. Turn 1: list_files to find the order export and the README.
2. read README.md: the export retried, so rows can repeat.
3. read orders/september-2026.csv and count the distinct Brindle & Co order_ids: CS-8812, CS-8817, CS-8821, CS-8824, CS-8831, CS-8835 = 6.
4. Turn 2 needs no further call: the same read holds Hartwell Bros' rows, and their distinct order_ids (CS-8815, CS-8826, CS-8833, CS-8837, CS-8841) give 5.

## Why the answer is unique
The question asks for orders, and the README states the export retried so some orders were written more than once. Each repeated row matches its original in every column, so the repeats are the same orders written twice, not new ones: Brindle & Co has 6 distinct order_ids and Hartwell Bros 5. Counting the 8 Brindle rows instead answers a question nobody asked.

## Five alternative phrasings of the task
1. crankset supplies brindle & co september orders
2. how many orders hartwell bros september
3. crankset september order book by customer
4. distinct orders for brindle and co
5. crankset supplies trade orders count

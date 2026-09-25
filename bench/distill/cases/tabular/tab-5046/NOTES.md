## Traps
- TR-MULTISRC: the order log holds which customer took how many packs of which product code but no money at all, while pack_prices.csv holds the only price for each code. The order log on its own yields a count of 245 packs rather than a value, and the price list on its own names no customer, so neither source alone can give the invoice figure.

## Reference solution
1. List the workspace: the August order lines, the price list and a short readme.
2. Read pack_prices.csv and note the price per pack of each product code.
3. Read order_lines_2026-08.csv, keep the Marlpit Nurseries rows and multiply the packs on each of them by the price of its product code: 1705.0 pounds.

## Why the answer is unique
A value needs both sources: the order log carries the packs and the product code of every line the customer ordered, and the price list carries the only figure for what a pack of that code costs. Prices do not vary by customer or date in this file, so matching the two on product code fixes the value of each line, and the Marlpit Nurseries lines come to 1705.0 pounds.

## Traps
- TR-MULTISRC: stock.csv has no category or price, catalog/items.csv has no quantities; using one file alone cannot give the value (summing Accessories quantities alone gives 1526 units, not money).

## Reference solution
1. data_query catalog/items.csv with filter {"category": "Accessories"}, select sku,list_price: 12 SKUs.
2. data_query inventory/stock.csv grouped by sku, operation sum, field qty.
3. calculator: sum of qty x list_price over the 12 Accessories SKUs = 68181.47.
4. (Optional) README for currency.
Final answer, 1-2 sentences: Accessories stock is worth GBP 68,181.47 at list price across Leeds, Bristol and Glasgow (quantities from inventory/stock.csv times prices from catalog/items.csv). Criteria: contains the total in either plain or comma form; data_query used; at most one read_file.

## Why the answer is unique
Each SKU has one price and one category; summing qty x price over the Accessories SKUs gives a single total.

## Traps
- TR-DECOY: K-2080 starts with K-208 and prices-2025.csv has an older K-208 price of 35.00.

## Reference solution
1. read_file data/prices.csv
Final answer: SKU K-208 的单价是 38.40（data/prices.csv；K-2080 是另一个 SKU，prices-2025.csv 是旧价）。

## Why the answer is unique
The user names data/prices.csv; the sku column holds K-208 exactly once.
Why bash is not the tool here: one named file and one fact, so read_file is the direct read. The turn forbids bash so the rows teach that bash being offered does not make it the default.

## Alternative phrasings
1. What does SKU K-208 cost per unit according to data/prices.csv?
2. Look up K-208 in prices.csv and give me its unit price.
3. How much is one K-208 in the current price table?
4. data/prices.csv: price of K-208?
5. Tell me the unit_price of K-208 in data/prices.csv.

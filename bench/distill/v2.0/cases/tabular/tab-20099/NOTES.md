## Traps
- The shell is missing: count with the table/search tools or by reading, not by a pipeline.

## Reference solution
data_query path=data/orders.csv filter={状态:已取消} operation=count -> 110

## Why the answer is unique
Exact match on the 状态 column of the one csv.

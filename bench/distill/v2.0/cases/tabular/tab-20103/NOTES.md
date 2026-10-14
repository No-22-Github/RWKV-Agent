## Traps
- The shell is missing: count with the table/search tools or by reading, not by a pipeline.

## Reference solution
data_query filter={渠道:电话} operation=avg field=时长分钟 -> 117.86

## Why the answer is unique
Exact channel match; mean of the 时长分钟 column rounded to two decimals.

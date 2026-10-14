## Traps
- The shell is missing: count with the table/search tools or by reading, not by a pipeline.

## Reference solution
data_query filter={level:warn} operation=count on events.jsonl -> 113 (or search_text)

## Why the answer is unique
level is an exact field of every record.

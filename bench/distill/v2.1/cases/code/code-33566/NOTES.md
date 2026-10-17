## Traps
TR-SUPERSEDE: load_batch failed then passed on retry.

## Reference solution
read log.

## Why the answer is unique
parse_quotes; load_batch timed out first.
Expected: parse_quotes; 3 cols; timeout

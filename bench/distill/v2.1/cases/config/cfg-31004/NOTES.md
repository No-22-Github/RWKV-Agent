## Traps
- TR-DECOY: pool_size: 10 appears under database, database.replica and cache.
- 1 file(s) change, 0 stay byte-identical.

## Reference solution
1. read_lines config/app.yaml
2. replace_lines 7
3. read back

## Why the answer is unique
Only the replica pool_size is 25.
Final answer should mention: 25

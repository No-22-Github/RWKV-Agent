## Traps
- TR-DECOY: LOG_LEVEL: info appears under three services.
- 1 file(s) change, 0 stay byte-identical.

## Reference solution
1. read_file docker-compose.yml
2. replace_lines on line 12
3. read back

## Why the answer is unique
Only the worker's LOG_LEVEL line changes to debug.
Final answer should mention: debug; worker

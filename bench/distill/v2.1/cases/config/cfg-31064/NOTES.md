## Traps
- TR-DECOY: line numbers drift by one after the first turn; retry blocks are duplicated.
- 1 file(s) change, 0 stay byte-identical.

## Reference solution
1. read_lines
2. replace 4-5
3. re-read
4. replace dead_letter enabled
5. read back the edited region and compare with the request

## Why the answer is unique
queue retry 5+jitter, dead_letter disabled.
Final answer should mention: jitter; enabled: false; jitter: true; max: 5

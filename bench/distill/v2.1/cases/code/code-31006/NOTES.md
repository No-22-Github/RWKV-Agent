## Traps
- TR-DECOY: 'TIMEOUT': 20 appears three times.
- 1 file(s) change, 0 stay byte-identical.

## Reference solution
1. read_lines src/settings.py
2. replace_lines 12
3. read back

## Why the answer is unique
Only line 12 changes to 'TIMEOUT': 120,.
Final answer should mention: 120

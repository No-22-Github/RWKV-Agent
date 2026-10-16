## Traps
- TR-DECOY: timeout = 30 appears in four sections.
- 1 file(s) change, 0 stay byte-identical.

## Reference solution
1. read_file settings.ini
2. replace line 9
3. read back the section

## Why the answer is unique
Only [cache] timeout becomes 5.
Final answer should mention: timeout = 5; [cache]; 15; 5

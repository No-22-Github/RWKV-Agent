## Traps
- TR-DECOY: overwriting the file with only the new entry loses 1.3.0 and 1.2.4.
- 1 file(s) change, 0 stay byte-identical.

## Reference solution
1. read_file CHANGELOG.md to see the current end
2. append_file
3. read back the tail

## Why the answer is unique
The original text must remain verbatim and the new lines must be present (contains).
Final answer should mention: 3

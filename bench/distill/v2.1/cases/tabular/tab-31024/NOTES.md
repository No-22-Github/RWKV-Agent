## Traps
- TR-DECOY: header and existing rows must stay; a rewrite with only the new row loses them.
- 1 file(s) change, 0 stay byte-identical.

## Reference solution
1. read_file members.csv to see the current end
2. append_file
3. read back the tail

## Why the answer is unique
The original text must remain verbatim and the new lines must be present (contains).
Final answer should mention: 4

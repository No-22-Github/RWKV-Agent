## Traps
- TR-DECOY: JSON lines must stay one per line, existing lines kept.
- 1 file(s) change, 0 stay byte-identical.

## Reference solution
1. read_file data/errors.jsonl to see the current end
2. append_file
3. read back the tail

## Why the answer is unique
The original text must remain verbatim and the new lines must be present (contains).
Final answer should mention: 3

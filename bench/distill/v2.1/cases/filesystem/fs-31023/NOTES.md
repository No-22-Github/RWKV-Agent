## Traps
- TR-DECOY: journal entries must not be rewritten.
- 1 file(s) change, 0 stay byte-identical.

## Reference solution
1. read_file logs/ops-journal.log to see the current end
2. append via append_file or bash >>
3. read back the tail

## Why the answer is unique
The original text must remain verbatim and the new lines must be present (contains).
Final answer should mention: 1.8.1; failover; 6

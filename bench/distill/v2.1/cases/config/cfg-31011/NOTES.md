## Traps
- TR-DECOY: three alerts share > 80 and for: 5m; turn 2 targets the same rule again.
- 1 file(s) change, 0 stay byte-identical.

## Reference solution
1. read_lines
2. replace line 8
3. turn 2: replace line 9
4. read back

## Why the answer is unique
Final HighMemory rule is expr > 90, for: 10m; others unchanged.
Final answer should mention: 90; 10m; 90

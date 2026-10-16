## Traps
- TR-DECOY: columns shift easily; qty vs loc.
- 1 file(s) change, 0 stay byte-identical.

## Reference solution
1. read_file
2. replace line 5
3. replace line 3
4. read back
5. read back the edited region and compare with the request

## Why the answer is unique
Two rows changed.
Final answer should mention: 800; 仓3; 800; A-101

## Traps
- TR-DECOY: three compile lines; recipe lines must keep the leading tab.
- 1 file(s) change, 0 stay byte-identical.

## Reference solution
1. read_lines Makefile
2. replace_lines 11 with tab-indented line
3. read back

## Why the answer is unique
Only line 11 gains the flag.
Final answer should mention: -fsanitize=address; app_test

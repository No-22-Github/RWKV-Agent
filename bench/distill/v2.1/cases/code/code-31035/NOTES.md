## Traps
- TR-DECOY: import line and call line are separate edits in each file.
- 4 file(s) change, 0 stay byte-identical.

## Reference solution
1. grep -rn fmt_date
2. edit 4 files
3. grep again

## Why the answer is unique
No fmt_date remains.
Final answer should mention: format_date; 4

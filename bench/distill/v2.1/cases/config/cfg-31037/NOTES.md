## Traps
- TR-READONLY: prod is held back by NOTES.txt; excluded file stays.
- 2 file(s) change, 2 stay byte-identical.

## Reference solution
1. read NOTES.txt
2. edit dev and staging
3. grep tag

## Why the answer is unique
dev and staging 3.5.0; prod unchanged.
Final answer should mention: dev; staging; 3.5.0

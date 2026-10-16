## Traps
- TR-DECOY: legacy-copy.sh shares the string and must stay.
- 3 file(s) change, 1 stay byte-identical.

## Reference solution
1. grep -rn old-nas
2. sed three files
3. grep again

## Why the answer is unique
Three files change.
Final answer should mention: new-nas; backup.sh; restore.sh

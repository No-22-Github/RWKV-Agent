## Traps
- TR-DECOY: two backup.sh lines differ only in time/target.
- 1 file(s) change, 0 stay byte-identical.

## Reference solution
1. bash sed on the s3 line
2. grep backup deploy/cron.txt

## Why the answer is unique
Only line 3 changes.
Final answer should mention: 45 3 * * *; s3

## Traps
- TR-DECOY: rotate-logs and sync-assets bracket the two lines with similar schedules; the range must be exactly the middle two lines.
- replace_lines must cover the whole run of 2 lines (start_line 3, end_line 4) and content must have 2 lines; a shorter range leaves old lines behind and a longer one eats the next block.

## Reference solution
1. Read etc/crontab.jobs; the target lines are 3-4.
2. replace_lines start_line 3, end_line 4 with:
   45 3 * * * /opt/jobs/vacuum-db.sh
   0 4 * * 6 /opt/jobs/full-backup.sh
3. Read etc/crontab.jobs back to confirm.
Final answer, one sentence: Updated etc/crontab.jobs lines 3-4 (2 lines), re-read the file to confirm. Criteria: file equals the expected text exactly.

## Why the answer is unique
The prompt names every new value and the block is identified unambiguously; all other lines stay byte-identical.

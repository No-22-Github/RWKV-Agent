## Traps
Slow query WARN at 02:10 is a decoy; api errors are a symptom; the first signal is the filesystem 100% line in system.log at 02:41, db FATAL at 02:43.

## Reference solution
grep ERROR/FATAL/WARN across logs, order by time.

## Why the answer is unique
Disk full from 02:41; API healthy 03:06.

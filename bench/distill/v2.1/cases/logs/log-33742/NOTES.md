## Traps
Queue overflow looks like the root cause; the lock holder is the backup.

## Reference solution
read cron WARN, backup lock lines.

## Why the answer is unique
data.lock held by backup 02:00-03:40.

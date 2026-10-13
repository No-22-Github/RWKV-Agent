## Traps
- Answer: 41.
- Data volume: 1 data files, 95 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `grep ' device=valve-' plant/alarms.log | grep -v ' sev=info ' | awk '{print $4}' | sort -u | wc -l` -> 41
Final answer: 41 distinct codes.

## Why the answer is unique
device, sev and ack are exact key=value fields; pump-12b is a different device.

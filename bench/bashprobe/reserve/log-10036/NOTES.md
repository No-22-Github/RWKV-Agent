## Traps
- Answer: valve-31.
- Data volume: 1 data files, 96 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `grep ' sev=critical ' plant/alarms.log | awk '{print $2}' | sort | uniq -c | sort -rn | head -3` -> valve-31
Final answer: valve-31 raised the most critical alarms.

## Why the answer is unique
device, sev and ack are exact key=value fields; pump-12b is a different device.

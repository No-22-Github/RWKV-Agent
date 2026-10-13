## Traps
- Answer: 16. TR-DECOY: matching pump-12b as well gives 23.
- Data volume: 1 data files, 93 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `grep ' device=pump-12 ' plant/alarms.log | grep ' sev=critical ' | grep -c ' ack=no$'` -> 16
Final answer: 16 unacknowledged critical alarms on pump-12 (pump-12b excluded).

## Why the answer is unique
device, sev and ack are exact key=value fields; pump-12b is a different device.

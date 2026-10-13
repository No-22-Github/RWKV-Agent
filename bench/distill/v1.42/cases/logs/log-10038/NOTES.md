## Traps
- Turn 1: 80.
- Turn 2: 26.
- Data volume: 1 data files, 95 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
Turn 1: bash: `grep ' device=boiler-2 ' plant/alarms.log | grep -c ' sev=warning '` -> 80
Turn 2: bash: `grep ' device=boiler-2 ' plant/alarms.log | grep ' sev=warning ' | awk '$1 >= "ts=2026-09-20"' | wc -l` -> 26
Final answer (last turn): 26 warnings on boiler-2 since 20 September.

## Why the answer is unique
device, sev and ack are exact key=value fields; pump-12b is a different device.

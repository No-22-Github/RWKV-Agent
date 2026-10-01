## Traps
- TR-HEADER: the mid-journal checkpoint record claims bus_error_sensors_dropped_total 88, a running total frozen at mid-day; the README marks checkpoints as non-events. The event records actually sum to 117.

## Reference solution
1. Read README.md: record shapes and the status of checkpoint records.
2. Search 'bus_error' and read the lines around the hits.
3. Take sensors_dropped from each event record with kind bus_error (all are nonzero).
4. The sum is 117.

## Why the answer is unique
Checkpoint records are excluded by the README, so only event records count; every bus_error event carries a nonzero sensors_dropped and no other kind contributes. The sum is 117.

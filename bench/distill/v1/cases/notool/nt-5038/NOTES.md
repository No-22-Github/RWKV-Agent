## Traps
- TR-NOTOOLNEED: the gate sheet and the offset table are in the workspace, and Kathmandu keeps a fixed quarter-hour offset. Reading the offset as a flat half hour gives 120 minutes.

## Reference solution
No steps; ref_calls is 0. 07:30 is 450 minutes; subtract the 345 minute offset. The answer is 105.

## Why the answer is unique
Kathmandu runs at UTC+05:45, so 07:30 local is 01:45 UTC, which is 105 minutes after midnight. 120 is what a flat half hour would give (07:30 minus 05:30); the offset table keys 05:45 to Kathmandu, and a gate booked against that row cannot be logged against an offset the table does not carry for the station.

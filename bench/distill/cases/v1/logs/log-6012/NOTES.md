## Traps
None. A yaw move produces one yaw_start line naming its turbine, and the question counts yaw_start lines of turbine T-2.

## Reference solution
1. List the workspace: README.md and logs/turbine-events.log.
2. Read README.md: each yaw move opens with a yaw_start line.
3. Read logs/turbine-events.log and count yaw_start lines with turbine=T-2 = 6.

## Why the answer is unique
Each yaw_start names exactly one turbine and its yaw_stop repeats the same turbine, so counting starts and counting stop-start pairs give the same number. The other turbines' lines and the single-line derate and fault_reset events fail the turbine filter. The answer is 6.
